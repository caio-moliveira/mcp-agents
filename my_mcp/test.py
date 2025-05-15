from fastmcp import Client
import asyncio


async def test():
    client = Client("http://127.0.0.1:8000/sse")
    async with client:
        print("Connected!")


asyncio.run(test())
