from fastapi import FastAPI
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any
from openai import OpenAI
import fitz
import threading
import uuid
import time
import json
import os
from dotenv import load_dotenv
from termcolor import colored
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

#uvicorn python_server:app --host 0.0.0.0 --port 3500 --reload 로 실행

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 Origin 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOAD_DIR = Path("../springboot-server/uploads/")
BASE_DIR = Path("book_analysis")
KNOWLEDGE_DIR = BASE_DIR / "knowledge_bases"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

progress_info = {}   # task_id -> {"current_page": x, "total_pages": y}
task_results = {}    # task_id -> 요약 결과 (list)

MODEL = "gpt-4o-mini"

class PageContent(BaseModel):
    has_content: bool
    knowledge: list[str]

def process_pdf(task_id: str, filename: str, start_page: int, end_page: int):
    pdf_path = UPLOAD_DIR / filename
    client = OpenAI()

    if not pdf_path.exists():
        print("파일을 찾을 수 없습니다.")
        return

    doc = fitz.open(str(pdf_path))
    total_pages = doc.page_count

    if start_page < 1 or end_page > total_pages or start_page > end_page:
        print("페이지 범위가 잘못되었습니다.")
        return

    pages_to_process = end_page - start_page + 1
    progress_info[task_id] = {"current_page": 0, "total_pages": pages_to_process}
    knowledge_base = []

    for idx, page_num in enumerate(range(start_page - 1, end_page)):
        page = doc[page_num]
        page_text = page.get_text()

        print(colored(f"\n📖 Processing page {page_num + 1}...", "yellow"))

        completion = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": """
                당신은 학습 도우미입니다. 제공된 페이지 텍스트를 분석하여 다음 지침을 따르세요:

                [건너뛸 페이지]
                - 목차
                - 장 목록
                - 인덱스 페이지
                - 공백 페이지
                - 저작권 정보
                - 출판사 정보
                - 참고문헌, 서지사항
                - 감사의 글

                [지식을 추출할 페이지]
                - 서문 내용 중 핵심 개념을 설명하는 부분
                - 본문의 주요 학습 내용
                - 핵심 정의와 개념
                - 중요한 주장이나 이론
                - 예시 및 사례 연구
                - 주요 연구 결과나 결론
                - 방법론 또는 분석 프레임워크
                - 비판적 해석이나 중요한 인용문

                [출력 형식]
                - `has_content` : 유의미한 학습 내용이 있으면 true, 아니면 false
                - `knowledge` : 학습 가능한 지식 포인트를 목록으로 추출
                - 구체적이고, 정확한 표현 사용
                - 중요한 용어는 원어 그대로 보존
                - 필요 시 간단한 설명도 추가

                [요약 작성 규칙]
                - 
                """},
                {"role": "user", "content": f"Page text: {page_text}"}
            ],
            response_format=PageContent
        )

        result = completion.choices[0].message.parsed
        if result.has_content:
            knowledge_base.extend(result.knowledge)

        # 페이지 하나 처리 끝났으니 업데이트
        progress_info[task_id]["current_page"] = idx + 1
        time.sleep(1)  # (실제 API 속도 조절용, 삭제해도 됨)

    # 전체 결과 저장
    task_results[task_id] = {"knowledge": knowledge_base}

    print(colored(f"✅ Finished processing {pages_to_process} pages!", "green"))

@app.get("/process")
def start_processing(filename: str, start_page: int = 1, end_page: int = 1):
    task_id = str(uuid.uuid4())

    thread = threading.Thread(target=process_pdf, args=(task_id, filename, start_page, end_page))
    thread.start()

    return {"message": "Processing started", "task_id": task_id}

@app.get("/progress")
def get_progress(task_id: str):
    if task_id not in progress_info:
        return {"error": "Task not found"}

    progress = progress_info[task_id]
    return {
        "current_page": progress["current_page"],
        "total_pages": progress["total_pages"]
    }

@app.get("/result")
def get_result(task_id: str):
    if task_id not in task_results:
        return {"error": "Task not completed or not found"}

    return task_results[task_id]

