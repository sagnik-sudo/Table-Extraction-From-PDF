import os
from camelot.core import TableList
from fastapi import FastAPI, UploadFile, File
import camelot
import shutil
import time
from fastapi import FastAPI
import pandas as pd
from pandas.core.frame import DataFrame
from fastapi.responses import FileResponse
from json_to_df import json_respone_to_df
import requests
import json

description = """
___This is a simple API that accepts a PDF file and fetch all table contents. Also, the API compares the output of Dexter and Camelot.___


### Upload PDF to Server
The PDF file is uploaded to the server.

### Upload PDF to Dexter
The PDF file is uploaded to Dexter and output is fetched.

### Fetch Tables from Server
The tables are fetched from the server and returned as a list of tables.


### Fetch Tables from Dexter
The tables are fetched from the dexter server and returned as a list of tables.

### Compare Output of Dexter vs Server
The tables are compared and the differences are returned as a table.

"""
app = FastAPI(title="Jupiter PDF",
    description=description,
    contact={
        "name": "Developers",
        "email": "sagnikd@buddi.ai;adithyab@buddi.ai"
    },
    version="Hackathon")

tables:TableList = None
filenm1 = ""
filenm2 = ""

def find_tables(loc) -> str:
    global tables
    return tables[loc].df.to_html(path = "")

@app.post("/camelot/uploadpdf",tags=["Upload PDF file"])
async def upload_pdf_to_server(file: UploadFile = File(...)):
    global tables
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ts = time.time()
    filename = f'{dir_path}/uploads/file{ts}{file.filename}'
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    tables = camelot.read_pdf(filename,pages='all')
    if tables is None:
        return {"Error": "No tables found. Please upload a PDF file."}
    return {"Upload Success" : {"Total tables extracted": tables.n}}

@app.post("/dexter/uploadpdf",tags=["Upload PDF file"])
async def dexter_upload_pdf(file: UploadFile = File(...)):
    output = requests.post("http://10.0.1.22:8000/extract_content", files={'file': file.file})
    outFileName=r"uploads/response_1635569329285.json"
    outFile=open(outFileName, "w")
    outFile.write(output.text)
    outFile.close()
    return {"Success":"Fetch Complete"}

@app.get("/camelot/gettables",tags=["View Tables"])
async def fetch_Tables():
    global tables
    ts = time.time()
    for i in range(tables.n):
        global filenm1
        filenm = f"outputs/file{ts}.csv"
        filenm1 = filenm
        pd.DataFrame([[f"Data Frame {i+1}"],[" "]],columns=["---------------------------------"]).to_csv(filenm,mode = 'a', index=False)
        tables[i].to_csv(filenm,mode = 'a', index = False)
    return FileResponse(filenm,media_type="application/text")

@app.get("/dexter/gettables",tags=["View Tables"])
async def dexter_Tables():
    filenm=json_respone_to_df(r"uploads\response_1635569329285.json")
    global filenm2
    filenm2 = filenm
    return FileResponse(filenm,media_type="application/text")



@app.get("/comparison",tags=["Compare Output of Dexter vs Camelot"])
async def comparison():
    global filenm1
    global filenm2
    with open(filenm1, 'r') as t1, open(filenm2, 'r') as t2:
        fileone = t1.readlines()
        filetwo = t2.readlines()
    ts = time.time()
    with open(f'outputs/outputs{ts}.csv', 'w') as outFile:
        for line in filetwo:
            if line not in fileone:
                outFile.write(line)
    return FileResponse(f'outputs/outputs{ts}.csv',media_type="application/text")