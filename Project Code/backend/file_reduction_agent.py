import os
import pandas as pd
import re
import ast
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_MOONSHOT_KIMI_DEV_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

def list_csv_files(directory):
    return [f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith('.csv')]

def get_file_summaries(files, csv_dir):
    summaries = []
    for file in files:
        path = os.path.join(csv_dir, file)
        try:
            df = pd.read_csv(path, nrows=3)
            summary = f"File: {file}\nColumns: {', '.join(df.columns)}\nSample:\n{df.head(1).to_dict(orient='records')[0]}"
        except Exception as e:
            summary = f"File: {file}\nCould not read file: {e}"
        summaries.append(summary)
    return summaries

def extract_list_from_response(response):
    match = re.search(r"\[.*?\]", response, re.DOTALL)
    if match:
        try:
            return ast.literal_eval(match.group(0))
        except Exception:
            return None
    return None

def reduce_files(csv_dir, n_keep):
    files = list_csv_files(csv_dir)
    merged_file = "__merged_all_data.csv"
    # Exclude merged file from selection and always keep it
    files_no_merged = [f for f in files if f != merged_file]
    if not files_no_merged:
        return {"error": "No CSV files found except the merged file."}
    summaries = get_file_summaries(files_no_merged, csv_dir)
    summaries_text = "\n\n".join(summaries)
    prompt = (
        f"You are a data analyst. Here are summaries of CSV files:\n\n"
        f"{summaries_text}\n\n"
        f"From the above, select the {n_keep} most important files to keep (based on file names and file data)."
        f"!IMPORTANT: The important files are the ones that contain sales, order and customer information or details about the product or industry-sub_domain."
        f"Make sure all the important files are kept in the directory"
        f"Return only the file names as a Python list, with no explanation or formatting, and do not include markdown or code blocks."
        f"For example: ['file1.csv', 'file2.csv']"
    )
    llm = ChatOpenAI(model="moonshotai/kimi-dev-72b:free", temperature=0)
    response = llm.invoke(prompt)
    response_text = str(response)
    keep_files = extract_list_from_response(response_text)
    if not keep_files or not isinstance(keep_files, list):
        return {"error": "Could not parse LLM response. Please check the output.", "llm_response": response_text}
    # Only keep up to n_keep files from files_no_merged
    keep_files = keep_files[:n_keep]
    # Always keep merged file
    keep_files.append(merged_file)
    remove_files = [f for f in files if f not in keep_files and f != merged_file]
    for f in remove_files:
        try:
            os.remove(os.path.join(csv_dir, f))
        except Exception:
            pass
    return {"kept": keep_files, "removed": remove_files}
