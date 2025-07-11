import os
from fastapi import FastAPI, Form, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from data_error_recognition_agent import (
    analyze_all_csv_files,
    create_merged_csv_agent,
    get_missing_values_by_prefix,
)
from data_modification_agent import modify_csv_file, process_instruction_file
from file_reduction_agent import reduce_files
from data_generation_agent_with_errors import generate_sql_for_industry_subdomain
from data_generation_agent import generate_ideal_sql_for_industry_subdomain 
import tempfile

CSV_FOLDER = r"D:\LangChain\TCS Project\backend\Industry-Sub_domain Data"
MERGED_FILE_NAME = "__merged_all_data.csv"
MERGED_FILE_PATH = os.path.join(CSV_FOLDER, MERGED_FILE_NAME)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cache agent
    app.state.cached_agent = create_merged_csv_agent()
    yield
    # Shutdown: (nothing needed, but you could clean up here)

app = FastAPI(lifespan=lifespan)

@app.get("/", include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/refresh-agent/")
def refresh_agent():
    app.state.cached_agent = create_merged_csv_agent()
    return {"status": "Agent and data refreshed"}

@app.post("/generate-ideal-data/")
def generate_ideal_sql(
    industry: str = Form(...),
    subdomain: str = Form(...)
):
    try:
        sql_output = generate_ideal_sql_for_industry_subdomain(industry, subdomain, CSV_FOLDER)
        return {"sql": sql_output}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    
@app.post("/generate-data-with-realistic-errors/")
def generate_sql(
    industry: str = Form(...),
    subdomain: str = Form(...)
):
    try:
        sql_output = generate_sql_for_industry_subdomain(industry, subdomain, CSV_FOLDER)
        return {"sql": sql_output}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/get-original-sql-contents/", response_class=PlainTextResponse)
def get_sql_contents():
    # List all files in the CSV_FOLDER directory
    sql_files = [f for f in os.listdir(CSV_FOLDER) if f.lower().endswith('.sql')]
    if not sql_files:
        return "No SQL file found in the directory."
    if len(sql_files) > 1:
        return "Multiple SQL files found. Please ensure only one SQL file is present."
    sql_file_path = os.path.join(CSV_FOLDER, sql_files[0])
    with open(sql_file_path, "r", encoding="utf-8") as f:
        contents = f.read()
    return contents

@app.get("/errors-analysis/")
def analyze_errors():
    return {"results": analyze_all_csv_files(CSV_FOLDER)}

@app.get("/missing-values/")
def missing_values():
    try:
        result = get_missing_values_by_prefix(MERGED_FILE_PATH)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/modify-data-interactive/")
def modify_data_interactive(
    filename: str = Form(...),
    instruction: str = Form(...)
):
    return modify_csv_file(CSV_FOLDER, filename, instruction)

@app.post("/modify-data-batch/")
async def modify_data_batch(
    instruction_file: UploadFile = File(...)
):
    filename = instruction_file.filename or "uploaded_file.txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[-1]) as tmp:
        tmp.write(await instruction_file.read())
        temp_path = tmp.name
    result = process_instruction_file(temp_path, CSV_FOLDER)
    os.remove(temp_path)
    return result

@app.post("/reduce-files/")
def reduce_files_endpoint(n_keep: int = Form(...)):
    result = reduce_files(CSV_FOLDER, n_keep)
    if not result or "error" in result:
        return {"error": "No result returned from reduce_files."}
    return result

@app.post("/ask-csv-question/")
def ask_csv_question(question: str = Form(...)):
    cached_agent = app.state.cached_agent
    if cached_agent is None:
        return {"error": "Agent not initialized."}
    try:
        result = cached_agent.invoke({"input": question}, handle_parsing_errors=True)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
