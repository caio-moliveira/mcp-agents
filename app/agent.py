from crewai import Agent, Task, Crew, Process
from crewai_tools import (
    FileReadTool,
    CodeInterpreterTool,
)
from client.client import load_supabase_tools, load_filesystem_tools
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
import logging


load_dotenv()

# Initialize logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Define the crew with two agents and two tasks
def create_crew():
    llm = ChatOpenAI(model="gpt-4.1-mini")

    csv_file_path = "data/cleaned/products.csv"
    target_table = "products"
    project_name = "mcp-project"
    project_id = os.getenv("SUPABASE_PROJECT_ID")

    file_tool = FileReadTool(file_path=csv_file_path)
    supabase_tools = load_supabase_tools(extra_tools=[file_tool])

    eda_tools = load_filesystem_tools(extra_tools="")

    # EDA Agent
    eda_agent = Agent(
        role="Data Exploration and Modeling Specialist",
        goal="Perform EDA and prepare the dataset for loading into Supabase",
        backstory="You are an expert in data exploration and modeling, specializing in preparing datasets for downstream tasks.",
        tools=eda_tools,
        llm=llm,
        verbose=True,
    )
    # Supabase Agent
    supabase_agent = Agent(
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
        tools=supabase_tools,
        verbose=True,
    )

    # EDA Task
    eda_task = Task(
        description="""
        Look for new files in the 'data/staging' folder. Perform the following tasks on each dataset:
        1. Generate summary statistics (mean, median, mode, etc.).
        2. Identify missing values and suggest imputation strategies.
        3. Detect duplicates and incorrect data types.
        4. Save findings in the 'data/findings' folder.
        5. If cleaning is required, save the cleaned dataset in the 'data/cleaned' folder.
        6. If no cleaning is required, move the file directly to the 'data/cleaned' folder.
        """,
        expected_output="Findings saved in 'data/findings' and cleaned dataset saved in 'data/cleaned'.",
        agent=eda_agent,
    )

    # Supabase Task
    supabase_task = Task(
        description=f"""
        You are assigned to ingest data from the cleaned CSV file at `{csv_file_path}` into the Supabase table `{target_table}`.
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
        agent=supabase_agent,
    )

    # Create the crew
    crew = Crew(
        agents=[eda_agent, supabase_agent],
        tasks=[eda_task, supabase_task],
        process=Process.sequential,
        verbose=True,
    )

    return crew


# Main function to execute the crew
def main():
    crew = create_crew()
    try:
        result = crew.kickoff()
        print("Crew execution completed successfully.", result)
    except Exception as e:
        print("Crew execution error:", e)


# Add the EDA agent to the main execution flow
if __name__ == "__main__":
    main()
