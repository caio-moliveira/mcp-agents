from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from app.client import load_supabase_tools
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv


load_dotenv()


def run_supabase_agent():
    llm = ChatOpenAI(model="gpt-4.1-mini")

    csv_file_path = "data/products.csv"
    target_table = "products"
    project_name = "mcp-project"
    project_id = os.getenv("SUPABASE_PROJECT_ID")

    file_tool = FileReadTool(file_path=csv_file_path)
    tools = load_supabase_tools(extra_tools=[file_tool])

    uploader_agent = Agent(
        role="Senior Data Integrity Engineer",
        goal="Ensure high-quality, consistent, and append-only data ingestion from CSV files into Supabase",
        backstory=(
            "You are a highly experienced data engineer and quality assurance expert. "
            "You are trusted to ingest data into production-grade systems with full ownership and accountability. "
            "You follow strict best practices for data integrity, never overwrite or delete existing records, "
            "and carefully validate data before allowing it into any database. "
            "Your goal is not speed, but correctness and auditability. "
            "If you find inconsistencies, schema mismatches, or invalid data, you must refuse to ingest and provide a clear explanation. "
            "When valid data is provided, you perform a safe, append-only insertion, deduplicating records if necessary."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=f"""
    You are assigned to ingest data from the CSV file at `{csv_file_path}` into the Supabase table `{target_table}`.
    Your Supabase project is `{project_name}` with ID `{project_id}`.

    Critical constraints:
    - You must **NEVER delete** or override data.
    - You must **validate** the CSV: required headers, consistent types, no missing critical values.
    - If any inconsistency or quality issue is found, **halt the process** and provide a clear, human-readable report of what failed.
    - You are responsible for ensuring the integrity of the data in the database.

    Your process:
    1. Read the file and parse it.
    2. Infer column types, and compare them against the target table (if it exists).
    3. If the table doesn’t exist, create it using the correct types and constraints.
    4. Compare existing records (based on all primary or unique columns) and insert only **new, non-duplicate** records.
    5. Provide a detailed success report including:
    - Number of new rows added
    - Table name
    - Timestamp of operation
    6. If data is invalid or problematic, stop the process, and return:
    - Reason(s) the file failed validation
    - Line/row references (if possible)
    - A suggestion of what the user must fix

    Never transform the data on your own. Either load it exactly as-is or reject it with full reasoning.
            """,
        expected_output=f"A report indicating either a successful append-only ingestion into `{target_table}`, or a detailed QA failure log explaining why it was rejected.",
        agent=uploader_agent,
    )

    crew = Crew(agents=[uploader_agent], tasks=[task], verbose=True)

    try:
        result = crew.kickoff()
        print(result)
    except Exception as e:
        print("Crew execution error:", e)


if __name__ == "__main__":
    run_supabase_agent()
