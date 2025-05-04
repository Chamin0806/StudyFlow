from fastapi import FastAPI, Query
from pathlib import Path
import fitz

# uvicorn main:app --host 0.0.0.0 --port 3500 --reload 명령어로 실행

app = FastAPI()

UPLOAD_DIR = Path("../springboot-server/uploads/")

@app.get("/process")
def process_pdf(filename: str):
    pdf_path = UPLOAD_DIR / filename

    if not pdf_path.exists():
        return {"error": "File not found"}

    doc = fitz.open(str(pdf_path))
    total_pages = doc.page_count

    # TODO: 여기서 페이지별로 분석하는 로직 실행해야함
    print(f"파일이름: {filename}")
    print(f"전체 페이지: {total_pages}")

    return {"message": "Processing started", "total_pages": total_pages}
