from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
from openai import OpenAI
import fitz  # PyMuPDF
from termcolor import colored
from datetime import datetime
import shutil

# source for the infinite descent book: https://infinitedescent.xyz/dl/infdesc.pdf

# Configuration Constants

import os
from dotenv import load_dotenv
load_dotenv()

PDF_NAME = "Database_3.pdf"
BASE_DIR = Path("book_analysis")
PDF_DIR = BASE_DIR / "pdfs"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_bases"
SUMMARIES_DIR = BASE_DIR / "summaries"
PDF_PATH = PDF_DIR / PDF_NAME
OUTPUT_PATH = KNOWLEDGE_DIR / f"{PDF_NAME.replace('.pdf', '_knowledge.json')}"
ANALYSIS_INTERVAL = 20  # Set to None to skip interval analyses, or a number (e.g., 10) to generate analysis every N pages
MODEL = "gpt-4o-mini"
ANALYSIS_MODEL = "o1-mini"
TEST_PAGES = 20  # Set to None to process entire book


class PageContent(BaseModel):
    has_content: bool
    knowledge: list[str]


def load_or_create_knowledge_base() -> Dict[str, Any]:
    if Path(OUTPUT_PATH).exists():
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_knowledge_base(knowledge_base: list[str]):
    output_path = KNOWLEDGE_DIR / f"{PDF_NAME.replace('.pdf', '')}_knowledge.json"
    print(colored(f"💾 Saving knowledge base ({len(knowledge_base)} items)...", "blue"))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"knowledge": knowledge_base}, f, indent=2)

def process_page(client: OpenAI, page_text: str, current_knowledge: list[str], page_num: int) -> list[str]:
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

            (주의) 페이지 전체를 요약하지 말고, 학습 가치가 있는 포인트만 뽑아내세요.
            """},
            {"role": "user", "content": f"Page text: {page_text}"}
        ],
        response_format=PageContent
    )
    
    result = completion.choices[0].message.parsed
    if result.has_content:
        print(colored(f"✅ Found {len(result.knowledge)} new knowledge points", "green"))
    else:
        print(colored("⏭️  Skipping page (no relevant content)", "yellow"))
    
    updated_knowledge = current_knowledge + (result.knowledge if result.has_content else [])
    
    # Update single knowledge base file
    save_knowledge_base(updated_knowledge)
    
    return updated_knowledge

def load_existing_knowledge() -> list[str]:
    knowledge_file = KNOWLEDGE_DIR / f"{PDF_NAME.replace('.pdf', '')}_knowledge.json"
    if knowledge_file.exists():
        print(colored("📚 Loading existing knowledge base...", "cyan"))
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(colored(f"✅ Loaded {len(data['knowledge'])} existing knowledge points", "green"))
            return data['knowledge']
    print(colored("🆕 Starting with fresh knowledge base", "cyan"))
    return []

def analyze_knowledge_base(client: OpenAI, knowledge_base: list[str]) -> str:
    if not knowledge_base:
        print(colored("\n⚠️  Skipping analysis: No knowledge points collected", "yellow"))
        return ""
        
    print(colored("\n🤔 Generating final book analysis...", "cyan"))
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """
            제공된 학습 내용을 기반으로, 간결하지만 자세한 최종 요약을 작성하세요.  
            결과는 **마크다운(Markdown) 형식**으로 작성합니다.

            [요약 작성 규칙]
            - ## 제목 형식으로 주요 주제를 구분하세요
            - ### 소제목을 사용하여 세부 내용을 정리하세요
            - 리스트는 - 기호로 정리하세요
            - 코드나 공식은 `코드 블록` 으로 표시하세요
            - 강조할 내용은 **굵게** 표시하세요
            - 용어 설명은 *이탤릭체*로 표시하세요
            - 중요한 메모는 > 인용구 형식으로 나타내세요

            [주의사항]
            - 결과물에는 "요약입니다" 같은 문구를 포함하지 마세요.
            - 불필요한 말머리나 결론 문구 없이, 요약된 내용만 출력하세요.
            - 최대한 자연스럽고 학습하기 좋은 한국어로 정리하세요.
            - 제일 마지막 줄에는, 요약한 내용과 관련이 있는 도서들의 목록을 추천 해 주세요.
            """},
            {"role": "user", "content": f"Analyze this content:\n" + "\n".join(knowledge_base)}
        ]
    )
    
    print(colored("✨ Analysis generated successfully!", "green"))
    return completion.choices[0].message.content

def setup_directories():
    # Clear all previously generated files
    for directory in [KNOWLEDGE_DIR, SUMMARIES_DIR]:
        if directory.exists():
            for file in directory.glob("*"):
                file.unlink()  # Delete all files in these directories
    
    # Create all necessary directories
    for directory in [PDF_DIR, KNOWLEDGE_DIR, SUMMARIES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Ensure PDF exists in correct location
    if not PDF_PATH.exists():
        source_pdf = Path(PDF_NAME)
        if source_pdf.exists():
            # Copy the PDF instead of moving it
            shutil.copy2(source_pdf, PDF_PATH)
            print(colored(f"📄 Copied PDF to analysis directory: {PDF_PATH}", "green"))
        else:
            raise FileNotFoundError(f"PDF file {PDF_NAME} not found")

def save_summary(summary: str, is_final: bool = False):
    if not summary:
        print(colored("⏭️  Skipping summary save: No content to save", "yellow"))
        return
        
    # Create markdown file with proper naming
    if is_final:
        existing_summaries = list(SUMMARIES_DIR.glob(f"{PDF_NAME.replace('.pdf', '')}_final_*.md"))
        next_number = len(existing_summaries) + 1
        summary_path = SUMMARIES_DIR / f"{PDF_NAME.replace('.pdf', '')}_final_{next_number:03d}.md"
    else:
        existing_summaries = list(SUMMARIES_DIR.glob(f"{PDF_NAME.replace('.pdf', '')}_interval_*.md"))
        next_number = len(existing_summaries) + 1
        summary_path = SUMMARIES_DIR / f"{PDF_NAME.replace('.pdf', '')}_interval_{next_number:03d}.md"
    
    # Create markdown content with metadata
    markdown_content = f"""# Book Analysis: {PDF_NAME}
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{summary}

---
*Analysis generated using AI Book Analysis Tool*
"""
    
    print(colored(f"\n📝 Saving {'final' if is_final else 'interval'} analysis to markdown...", "cyan"))
    with open(summary_path, 'w', encoding='utf-8') as f:  # Added encoding='utf-8'
        f.write(markdown_content)
    print(colored(f"✅ Analysis saved to: {summary_path}", "green"))

def print_instructions():
    print(colored("""
📚 PDF 책 분석 도구 📚
---------------------------
1. 분석할 PDF 파일을 이 스크립트와 같은 폴더에 넣으세요.
2. 코드 상단의 PDF_NAME 값을 PDF 파일 이름으로 수정하세요.
3. 이 프로그램은 다음 작업을 수행합니다:
   - 책을 페이지 단위로 분석
   - 주요 학습 포인트(지식) 추출 및 저장
   - 지정된 간격마다 중간 요약 생성 (설정 시)
   - 전체 책에 대한 최종 요약 리포트 생성

[설정 옵션]
- ANALYSIS_INTERVAL: None으로 설정하면 중간 요약을 생략하고, 숫자로 설정하면 N페이지마다 요약 생성
- TEST_PAGES: None으로 설정하면 전체 책을 처리하고, 숫자로 설정하면 일부 페이지만 분석

계속하려면 Enter 키를 누르세요. 종료하려면 Ctrl+C를 누르세요.
""", "cyan"))

def main():
    try:
        print_instructions()
        input()
    except KeyboardInterrupt:
        print(colored("\n❌ Process cancelled by user", "red"))
        return

    setup_directories()
    client = OpenAI()
    
    # Load or initialize knowledge base
    knowledge_base = load_existing_knowledge()
    
    pdf_document = fitz.open(PDF_PATH)
    pages_to_process = TEST_PAGES if TEST_PAGES is not None else pdf_document.page_count
    
    print(colored(f"\n📚 Processing {pages_to_process} pages...", "cyan"))
    for page_num in range(min(pages_to_process, pdf_document.page_count)):
        page = pdf_document[page_num]
        page_text = page.get_text()
        
        knowledge_base = process_page(client, page_text, knowledge_base, page_num)
        
        # Generate interval analysis if ANALYSIS_INTERVAL is set
        if ANALYSIS_INTERVAL:
            is_interval = (page_num + 1) % ANALYSIS_INTERVAL == 0
            is_final_page = page_num + 1 == pages_to_process
            
            if is_interval and not is_final_page:
                print(colored(f"\n📊 Progress: {page_num + 1}/{pages_to_process} pages processed", "cyan"))
                interval_summary = analyze_knowledge_base(client, knowledge_base)
                save_summary(interval_summary, is_final=False)
        
        # Always generate final analysis on last page
        if page_num + 1 == pages_to_process:
            print(colored(f"\n📊 Final page ({page_num + 1}/{pages_to_process}) processed", "cyan"))
            final_summary = analyze_knowledge_base(client, knowledge_base)
            save_summary(final_summary, is_final=True)
    
    print(colored("\n✨ Processing complete! ✨", "green", attrs=['bold']))

if __name__ == "__main__":
    main()
