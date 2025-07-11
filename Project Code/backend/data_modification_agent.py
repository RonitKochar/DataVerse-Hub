import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_MISTRAL_SMALL_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

def list_csv_files(directory):
    return [f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith('.csv')]

def process_instruction_file(instruction_file, csv_dir):
    try:
        with open(instruction_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        return {"error": f"Could not read file '{instruction_file}': {e}"}
    if not lines:
        return {"error": "Instruction file is empty."}
    files = set(list_csv_files(csv_dir))
    llm = ChatOpenAI(model="mistralai/mistral-small-3.1-24b-instruct:free", temperature=0)
    agents = {}
    results = []
    for idx, line in enumerate(lines, 1):
        if ':' not in line:
            results.append({
                "line": idx,
                "status": "skipped",
                "reason": "missing colon",
                "line_content": line
            })
            continue
        filename, instruction = line.split(':', 1)
        filename = filename.strip()
        instruction = instruction.strip()
        if filename not in files:
            results.append({
                "line": idx,
                "status": "skipped",
                "reason": f"CSV file '{filename}' not found",
                "line_content": line
            })
            continue
        file_path = os.path.join(csv_dir, filename)
        if filename not in agents:
            agents[filename] = create_csv_agent(
                llm, file_path, verbose=False, allow_dangerous_code=True
            )
        agent_executor = agents[filename]
        response = agent_executor.invoke({"input": instruction})
        tool = agent_executor.tools[0]
        try:
            if hasattr(tool, "df"):
                df = tool.df
                df.to_csv(file_path, index=False)
            elif hasattr(tool, "locals") and "df" in tool.locals:
                df = tool.locals["df"]
                df.to_csv(file_path, index=False)
            elif hasattr(tool, "_locals") and "df" in tool._locals:
                df = tool._locals["df"]
                df.to_csv(file_path, index=False)
            else:
                results.append({
                    "line": idx,
                    "status": "warning",
                    "reason": "No DataFrame found to save.",
                    "line_content": line
                })
                continue
        except Exception as e:
            results.append({
                "line": idx,
                "status": "warning",
                "reason": f"Could not save changes: {e}",
                "line_content": line
            })
            continue
        results.append({
            "line": idx,
            "status": "success",
            "output": response.get("output"),
            "line_content": line
        })
    return results

def modify_csv_file(csv_dir, filename, instruction):
    files = set(list_csv_files(csv_dir))
    if filename not in files:
        return {"error": f"CSV file '{filename}' not found."}
    file_path = os.path.join(csv_dir, filename)
    llm = ChatOpenAI(model="mistralai/mistral-small-3.1-24b-instruct:free", temperature=0)
    agent_executor = create_csv_agent(
        llm, file_path, verbose=False, allow_dangerous_code=True
    )
    response = agent_executor.invoke({"input": instruction})
    tool = agent_executor.tools[0]
    try:
        if hasattr(tool, "df"):
            df = tool.df
            df.to_csv(file_path, index=False)
        elif hasattr(tool, "locals") and "df" in tool.locals:
            df = tool.locals["df"]
            df.to_csv(file_path, index=False)
        elif hasattr(tool, "_locals") and "df" in tool._locals:
            df = tool._locals["df"]
            df.to_csv(file_path, index=False)
        else:
            return {"error": "No DataFrame found to save."}
    except Exception as e:
        return {"error": f"Could not save changes: {e}"}
    return {"status": "success", "output": response.get("output")}
