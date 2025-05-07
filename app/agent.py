from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from app.client import load_supabase_tools
from langchain_openai import ChatOpenAI


def run_supabase_agent():
    llm = ChatOpenAI(model="gpt-4.1-mini")

    csv_file_path = "data/products.csv"
    target_table = "products"

    file_tool = FileReadTool(file_path=csv_file_path)
    tools = load_supabase_tools(extra_tools=[file_tool])  # ✅ pass in file tool

    uploader_agent = Agent(
        role="SupabaseUploader",
        goal="Upload CSV data to Supabase",
        backstory="You are responsible for creating tables and uploading data from local files into Supabase.",
        tools=tools,
        llm=llm,
        verbose=True,
    )

    task = Task(
        description=f"""
The CSV file is located at `{csv_file_path}`.

1. Read the file to determine the column names and data types.
2. Check if the Supabase table `{target_table}` exists.
3. If not, create it using the schema from the CSV.
4. Insert all rows from the file into the table.

Do not modify the data. Upload it as-is.
        """,
        expected_output=f"The CSV file `{csv_file_path}` has been successfully uploaded to the Supabase table `{target_table}`.",
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
