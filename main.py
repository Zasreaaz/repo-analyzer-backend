import io
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, Form
from pypdf import PdfReader

from agent.loop import run_agent

app = FastAPI()


@app.post("/analyze")
async def analyze(pdf: UploadFile, owner: str = Form(...), repo: str = Form(...)):
    pdf_bytes = await pdf.read()
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assignment_text = "\n".join(page.extract_text() or "" for page in reader.pages)

    return run_agent(assignment_text, owner, repo)