from fastapi import FastAPI, Query
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
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("../springboot-server/uploads/")
BASE_DIR = Path("book_analysis")
KNOWLEDGE_DIR = BASE_DIR / "knowledge_bases"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

progress_info = {}
task_results = {}

MODEL = "gpt-4o-mini"

class PageContent(BaseModel):
    has_content: bool
    knowledge: list[str]

def process_pdf(task_id: str, filename: str, start_page: int, end_page: int, recommend: bool, question: bool):
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
    progress_info[task_id] = {"current_page": 0, "total_pages": pages_to_process, "done": False}
    knowledge_base = []

    for idx, page_num in enumerate(range(start_page - 1, end_page)):
        page = doc[page_num]
        page_text = page.get_text()

        print(colored(f"\n📖 Processing page {page_num + 1}...", "yellow"))

        completion = client.beta.chat.completions.parse(
            model=MODEL,
            messages=[
                {"role": "system", "content": "당신은 학습 도우미입니다. 페이지 텍스트에서 학습 가능한 지식을 추출하세요."},
                {"role": "user", "content": f"Page text: {page_text}"}
            ],
            response_format=PageContent
        )

        result = completion.choices[0].message.parsed
        if result.has_content:
            knowledge_base.extend(result.knowledge)

        progress_info[task_id]["current_page"] = idx + 1
        time.sleep(1)

    summary_prompt = [
        {"role": "system", "content": """
            다음 학습 내용을 기반으로 아래 형식에 맞게 JSON으로 요약하세요:
            knowledge항목은 json을 기반으로 **마크다운(Markdown) 형식**으로 작성합니다.

            [요약 작성 규칙]
            - ## 제목 형식으로 주요 주제를 구분하세요
            - ### 소제목을 사용하여 세부 내용을 정리하세요
            - 리스트는 - 기호로 정리하세요
            - 코드나 공식은 `코드 블록` 으로 표시하세요
            - 강조할 내용은 **굵게** 표시하세요
            - 용어 설명은 *이탤릭체*로 표시하세요
            - 중요한 메모는 > 인용구 형식으로 나타내세요
            

            {{
                "knowledge": [...],
                "recommendation": {"제목": "링크", ...},
                "questions": {{"1": {{"문제": "...", "정답": "..."}}, ...}}
            }}
            'recommendation'과 'questions'는 사용자가 요청한 경우에만 포함하세요.
            recommendation에는 관련 도서, 자료 등을 넣고, 링크에는 실제 작동하는 링크를 출력하세요.
            JSON 이외의 텍스트는 절대 출력하지 마세요.
        """},
        {"role": "user", "content": json.dumps({
            "knowledge": knowledge_base,
            "include_recommendation": recommend,
            "include_questions": question
        })}
    ]

    try:
        ai_response = client.chat.completions.create(
            model=MODEL,
            messages=summary_prompt
        )
        combined_json = json.loads(ai_response.choices[0].message.content)
    except Exception as e:
        print("요약 파싱 실패:", e)
        combined_json = {
            "knowledge": knowledge_base,
            "recommendation": {"오류": "추천 자료 파싱 실패"} if recommend else {},
            "questions": {"오류": "문제 생성 실패"} if question else {}
        }

    task_results[task_id] = combined_json
    progress_info[task_id]["done"] = True
    print(colored(f"✅ Finished processing {pages_to_process} pages!", "green"))

@app.get("/process")
def start_processing(
    filename: str,
    start_page: int = 1,
    end_page: int = 1,
    recommend: bool = Query(False),
    question: bool = Query(False)
):
    task_id = str(uuid.uuid4())
    thread = threading.Thread(target=process_pdf, args=(task_id, filename, start_page, end_page, recommend, question))
    thread.start()
    return {"message": "Processing started", "task_id": task_id}

@app.get("/progress")
def get_progress(task_id: str):
    if task_id not in progress_info:
        return {"error": "Task not found"}
    return progress_info[task_id]

@app.get("/result")
def get_result(task_id: str):
    if task_id not in task_results:
        return {"error": "Task not completed or not found"}
    return task_results[task_id]
