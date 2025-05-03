# 📚 PDF 요약 웹사이트 프로젝트

## 프로젝트 소개

이 프로젝트는 다양한 오픈소스 소프트웨어를 결합하여,  
**PDF 파일을 페이지 단위로 분석하고 요약하는 웹사이트**를 만드는 것을 목표로 합니다.

본 과제는 GitHub를 통한 협업 경험과 오픈소스 소프트웨어의 실질적 활용 능력을 기르는 데 중점을 둡니다.

---

## 주요 기능

- 사용자가 PDF 파일을 업로드
- PDF를 한 페이지씩 읽어 분석
- 각 페이지에 대해 핵심 내용을 추출하여 요약
- 전체 요약본 제공
- 웹 인터페이스를 통한 결과 출력
- PDF 파일이 학습자료라면, 관련 내용의 도서 추천

---

## 사용 기술

| 영역 | 사용 오픈소스 및 기술 |
|:---|:---|
| 백엔드 (Python 서버) | FastAPI / PyMuPDF(fitz) / Pydantic |
| 인공지능 요약 | OpenAI API (gpt-4o-mini, o1-mini) |
| 프론트엔드 (웹사이트) | HTML / CSS / JavaScript |
| 협업 도구 | Git / GitHub |

---

## 오픈소스 소프트웨어 결합 및 수정 내역
- **AI-reads-books-page-by-page**
  - fitz와 OpenAI Python 라이브러리를 활용하여 PDF를 요약해주는 오픈소스 소프트웨어
  - https://github.com/echohive42/AI-reads-books-page-by-page
- **PyMuPDF** (fitz)
  - PDF 파일에서 텍스트 추출 기능 활용
  - 특정 페이지 단위 분석 기능 추가 및 튜닝
- **OpenAI Python 라이브러리**
  - 요약 요청 로직 커스터마이징 (분할 요약, 간격별 요약 처리)
- **FastAPI**
  - 파일 업로드 및 요약 결과 반환 API 서버로 활용
- **dotenv**
  - API 키 관리 및 환경변수 보안 강화
- (추가 수정사항 발생 시, 별도로 상세 기록 예정)

---

