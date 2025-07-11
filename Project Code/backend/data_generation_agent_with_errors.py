import os
import csv
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

CSV_FOLDER = r"D:\PROJECTS\DataVerse Hub\Project Code\backend\Industry-Sub_domain Data"

def generate_sales_sql(question: str, csv_folder: str) -> str:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    load_dotenv()
    os.environ["OPENAI_API_KEY"]  = os.getenv("MENTOR_API_KEY")
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

    template = """
    You are an expert SQL database designer and data generator.

    Based on the user's input, generate:
    1. At least 7 well-structured CREATE TABLE statements.
    2. At least 7 INSERT INTO statements per table (≥7 rows per table).
    3. All values must look realistic and relevant to the user's industry and sub-domain.
    4. IMPORTANT: In every table, at least 2 rows must contain realistic outlier values. Outliers should be values that are plausible but unusual or erroneous for the column, such as:
    - Numeric values that are just outside the normal range (e.g., negative numbers for sales, extremely high prices, track durations of 0 or 9999 seconds)
    - Typos, truncated, or excessively long strings in text fields (e.g., "Taylr Swft", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    - Unexpected but possible values in categorical fields (e.g., "XX" for country, "Unknown" or "Experimental" for genre)
    - Dates that are plausible but odd (e.g., 1900-01-01, 2099-12-31, or swapped month/day)
    - NULLs in columns where NULL is allowed
    - Duplicated or missing values in non-primary key fields
    5. In every table, at least 2 rows must contain NULL values in columns where NULLs are allowed.
    6. The rest of the data should be plausible and typical for the domain.
    7. Do NOT use placeholder names like "Outlier1" or "Outlier2". Make outliers look like real-world data errors or rare cases.

    Strict formatting rules:
    - DO NOT use markdown formatting (no triple backticks).
    - DO NOT include explanations or prefaces like “Here is”.
    - ONLY return the SQL, starting at Final Answer.

    Use this ReAct format:

    Question: {input}
    Thought: I understand the industry and sub-domain context.
    Action: None
    Action Input: None
    Observation: None
    Thought: Now I will generate the SQL code.
    Final Answer:
    <Only raw SQL here>

    Available tools: {tool_names}
    {tools}
    {agent_scratchpad}
    """

    prompt = PromptTemplate.from_template(template)

    llm = ChatOpenAI(
        model="mistralai/mistral-small-3.1-24b-instruct:free",
        temperature=0,
    )

    agent = create_react_agent(llm=llm, prompt=prompt, tools=[])
    executor = AgentExecutor(agent=agent, tools=[], verbose=True, handle_parsing_errors=True, max_iterations=5)
    
    result = executor.invoke({"input": question})
    output = result["output"]

    output = output.replace("``````", "").strip()
    save_insert_statements_to_csv(output, csv_folder)
    save_sql_to_file(output, csv_folder)

    return output

def save_insert_statements_to_csv(sql_text: str, csv_folder: str):
    insert_pattern = re.compile(
        r"INSERT INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*((?:\([^;]+?\))(?:\s*,\s*\([^;]+?\))*)\s*;",
        re.IGNORECASE | re.DOTALL
    )

    os.makedirs(csv_folder, exist_ok=True)

    matches = insert_pattern.finditer(sql_text)
    found_any = False

    for match in matches:
        found_any = True
        table_name = match.group(1)
        columns = [col.strip() for col in match.group(2).split(",")]
        values_block = match.group(3).replace('\n', ' ')

        value_rows = re.findall(r"\(([^)]+)\)", values_block)
        rows = []
        for value_str in value_rows:
            values = [v.strip().strip("'").strip('"') for v in re.split(r",(?=(?:[^']*'[^']*')*[^']*$)", value_str)]
            rows.append(values)

        filename = os.path.join(csv_folder, f"{table_name.lower()}_data.csv")
        with open(filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

    if not found_any:
        print("No INSERT INTO statements found in the SQL output.")

def save_sql_to_file(sql_text: str, csv_folder: str):
    file_path = os.path.join(csv_folder, "create_insert_statements.sql")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(sql_text)
        
def clear_directory_of_data_files(directory):
    # Remove all CSV and SQL files in the directory
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.csv', '.sql')):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
            except Exception:
                pass  # Optionally, log the error

def generate_sql_for_industry_subdomain(industry: str, subdomain: str, csv_folder: str) -> str:
    clear_directory_of_data_files(csv_folder)
    
    if not industry.strip():
        raise ValueError("Industry cannot be empty.")
    if not subdomain.strip():
        raise ValueError("Sub-domain cannot be empty.")

    user_question = (
        f"Generate a realistic SQL database for the '{industry}' industry focusing on the '{subdomain}' sub-domain. "
        "Include at least 7 tables and 7 rows per table."
    )
    output = generate_sales_sql(user_question, csv_folder)
    return output
