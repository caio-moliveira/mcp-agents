# app/mcp_client.py

from pydantic_ai import RunContext, Tool as PydanticTool
from pydantic_ai.tools import ToolDefinition
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool
from contextlib import AsyncExitStack
from typing import Any, List
import asyncio
import logging
import shutil
import json

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class MCPClient:
    def __init__(self) -> None:
        self.servers: List[MCPServer] = []
        self.config: dict[str, Any] = {}
        self.tools: List[PydanticTool] = []
        self.exit_stack = AsyncExitStack()

    def load_servers(self, config_path: str) -> None:
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.servers = [
            MCPServer(name, cfg)
            for name, cfg in self.config.get("mcpServers", {}).items()
        ]

    async def start(self) -> List[PydanticTool]:
        self.tools = []
        for server in self.servers:
            try:
                await server.initialize()
                tools = await server.create_pydantic_ai_tools()
                self.tools.extend(tools)
            except Exception as e:
                logging.error(f"[MCPClient] Failed to start server {server.name}: {e}")
                await self.cleanup_servers()
        return self.tools

    async def cleanup_servers(self) -> None:
        for server in self.servers:
            try:
                await server.cleanup()
            except Exception as e:
                logging.warning(f"[MCPClient] Cleanup warning for {server.name}: {e}")

    async def cleanup(self) -> None:
        await self.cleanup_servers()
        await self.exit_stack.aclose()


class MCPServer:
    def __init__(self, name: str, config: dict[str, Any]) -> None:
        self.name = name
        self.config = config
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self._cleanup_lock = asyncio.Lock()

    async def initialize(self) -> None:
        command = shutil.which(self.config["command"]) or self.config["command"]
        server_params = StdioServerParameters(
            command=command,
            args=self.config["args"],
            env=self.config.get("env", None),
        )

        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()
            self.session = session
        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize MCP server {self.name}: {e}")

    async def create_pydantic_ai_tools(self) -> List[PydanticTool]:
        tools = (await self.session.list_tools()).tools
        return [self._create_tool_instance(tool) for tool in tools]

    def _create_tool_instance(self, tool: MCPTool) -> PydanticTool:
        async def execute_tool(**kwargs: Any) -> Any:
            return await self.session.call_tool(tool.name, arguments=kwargs)

        async def prepare_tool(
            ctx: RunContext, tool_def: ToolDefinition
        ) -> ToolDefinition:
            tool_def.parameters_json_schema = tool.inputSchema
            return tool_def

        return PydanticTool(
            execute_tool,
            name=tool.name,
            description=tool.description or "",
            takes_ctx=False,
            prepare=prepare_tool,
        )

    async def cleanup(self) -> None:
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
            except Exception as e:
                logging.error(f"[MCPServer] Error cleaning up {self.name}: {e}")
