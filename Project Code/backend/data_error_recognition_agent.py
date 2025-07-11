import os
import atexit
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_csv_agent
from langchain_experimental.tools import PythonREPLTool

# Directory containing CSV files
CSV_FOLDER = r"D:\LangChain\TCS Project\backend\Industry-Sub_domain Data"
MERGED_FILE_NAME = "__merged_all_data.csv"
temp_merged_path = os.path.join(CSV_FOLDER, MERGED_FILE_NAME)

def cleanup():
    if os.path.exists(temp_merged_path):
        try:
            os.remove(temp_merged_path)
        except Exception:
            pass

atexit.register(cleanup)

def parse_dates_with_multiple_formats(series):
    import dateutil.parser
    parsed_dates = []
    for val in series:
        parsed = None
        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y/%m/%d']:
            try:
                parsed = pd.to_datetime(val, format=fmt, errors='raise')
                break
            except Exception:
                continue
        if parsed is None:
            try:
                parsed = dateutil.parser.parse(val)
            except Exception:
                parsed = pd.NaT
        parsed_dates.append(parsed)
    return pd.Series(parsed_dates)

def analyze_csv_file(file_path):
    df = pd.read_csv(file_path)
    analysis = {}
    analysis['file_name'] = os.path.basename(file_path)
    analysis['num_rows'] = df.shape[0]
    analysis['num_columns'] = df.shape[1]
    analysis['columns'] = list(df.columns)
    missing_data = df.isnull().sum()
    analysis['missing_data'] = missing_data[missing_data > 0].to_dict()
    outliers = {}
    for col in df.select_dtypes(include=[float, int, np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outlier_values = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col].tolist()
        if outlier_values:
            outliers[col] = outlier_values
    for col in df.select_dtypes(include=['object']).columns:
        try:
            dates = parse_dates_with_multiple_formats(df[col])
            if dates.notnull().any():
                outlier_dates = dates[(dates < pd.Timestamp('1900-01-01')) | (dates > pd.Timestamp('2100-01-01'))]
                if not outlier_dates.empty:
                    outliers[col] = [str(d) for d in outlier_dates.dt.strftime('%Y-%m-%d')]
        except Exception:
            pass
    analysis['outliers'] = outliers
    suspicious_values = {}
    suspicious_list = ['Unknown', 'unknown', 'XX', 'NULL', 'null', None]
    for col in df.select_dtypes(include=['object']).columns:
        suspicious_vals = df[col][df[col].isin(suspicious_list)].dropna().unique().tolist()
        if suspicious_vals:
            suspicious_values[col] = suspicious_vals
    analysis['suspicious_values'] = suspicious_values
    return analysis

def analyze_all_csv_files(csv_folder):
    results = []
    for filename in os.listdir(csv_folder):
        if filename.lower().endswith('.csv') and filename != MERGED_FILE_NAME:
            file_path = os.path.join(csv_folder, filename)
            try:
                analysis = analyze_csv_file(file_path)
                results.append(analysis)
            except Exception as e:
                results.append({'file_name': filename, 'error': str(e)})
    return results

def load_and_prepare_csvs(csv_folder):
    csv_files = [f for f in os.listdir(csv_folder)
                 if f.lower().endswith('.csv') and f != MERGED_FILE_NAME]
    dataframes = {}
    for fname in csv_files:
        path = os.path.join(csv_folder, fname)
        try:
            df = pd.read_csv(path)
            prefix = os.path.splitext(fname)[0]
            df = df.add_prefix(f"{prefix}__")
            dataframes[fname] = df
        except Exception:
            pass
    return dataframes

def merge_dataframes(dataframes):
    if not dataframes:
        return None
    dfs = list(dataframes.values())
    merged = pd.concat(dfs, axis=1)
    return merged

def create_merged_csv_agent(model_id="mistralai/mistral-small-3.2-24b-instruct:free"):
    load_dotenv()
    os.environ["OPENAI_API_KEY"] = os.getenv("MENTOR_API_KEY")
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    dataframes = load_and_prepare_csvs(CSV_FOLDER)
    merged_df = merge_dataframes(dataframes)
    if merged_df is None or merged_df.empty:
        return None
    merged_df.to_csv(temp_merged_path, index=False)
    csv_agent = create_csv_agent(
        llm=ChatOpenAI(temperature=0, model=model_id),
        path=temp_merged_path,
        verbose=True,
        allow_dangerous_code=True,
    )
    return csv_agent

def query_merged_csv_agent(question, model_id="moonshotai/kimi-dev-72b:free"):
    agent = create_merged_csv_agent(model_id=model_id)
    if agent is None:
        return {"error": "No CSV files found or data could not be loaded."}
    try:
        result = agent.invoke({"input": question}, handle_parsing_errors=True)
        return {"output": result.get("output", "")}
    except Exception as e:
        return {"error": str(e)}

def get_missing_values_by_prefix(merged_file_path):
    df = pd.read_csv(merged_file_path)
    prefixes = {col.split('__', 1)[0] for col in df.columns}
    missing_values = {}
    for prefix in prefixes:
        cols = [col for col in df.columns if col.startswith(f"{prefix}__")]
        missing = df[cols].isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            missing_values[prefix] = missing.to_dict()
    return missing_values
