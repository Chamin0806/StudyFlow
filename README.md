# 📚 PDF 요약 웹사이트 프로젝트

## 프로젝트 소개

이 프로젝트는 다양한 오픈소스 소프트웨어를 결합하여,  
**PDF 파일을 페이지 단위로 분석하고 요약하는 웹사이트**를 만드는 것을 목표로 합니다.

본 과제는 GitHub를 통한 협업 경험과 오픈소스 소프트웨어의 실질적 활용 능력을 기르는 데 중점을 둡니다.

---
## 👥 역할 분담

| 이름         | 역할 내용 | 
|--------------|-----------|
| **손차민 (조장)** | - 프로젝트 총괄 관리(PM)<br>- 백엔드 API 설계 및 FastAPI 서버 구축<br>- Thymeleaf사용 프로젝트 구조 설계| 프론트엔드 구현
| **이상민**       | - OpenAI 요약 요청 분할 처리 및 프롬프트 최적화<br>- dotenv 기반 환경 변수 및 배포 자동화 지원 | 프론트엔드 구현 <br>- 발표자료 준비
| **현주호**       | - 프론트엔드 구현 (파일 업로드 UI, 결과 출력)<br>- 사용자 인터페이스 개선 <br>- github wiki 탭 작성


> 💡 역할은 일부 협업 및 분담을 통해 유동적으로 조정되었으며, 본인의 역할이 아닌 부분에서도 전원 개발에 기여하였습니다.

---

## 주요 기능

- 사용자가 PDF 파일(학습자료)을 업로드
- PDF를 한 페이지씩 읽어 분석
- 각 페이지에 대해 핵심 내용을 추출하여 요약
- 전체 요약본 제공
- 웹 인터페이스를 통한 결과 출력
- 옵션에 따라 관련 자료 또는 학습에 도움되는 예제 문제 생성

---

## 사용 기술

| 영역 | 사용 오픈소스 및 기술 |
|:---|:---|
| 백엔드 (Python 서버) | FastAPI / PyMuPDF(fitz) / Pydantic |
| 인공지능 요약 | OpenAI API (gpt-4o-mini, o1-mini) |
| 프론트엔드 (웹사이트) | HTML / CSS / JavaScript / Thymeleaf|
| 협업 도구 | GitHub |

---

## 오픈소스 소프트웨어 결합 및 수정 내역

- **AI-reads-books-page-by-page**
  - fitz와 OpenAI Python 라이브러리를 활용하여 PDF를 요약해주는 오픈소스 소프트웨어
  - https://github.com/echohive42/AI-reads-books-page-by-page

- **PyMuPDF (fitz)**
  - PDF 파일에서 텍스트 추출 기능 활용
  - 특정 페이지 단위 분석 기능 추가 및 튜닝

- **OpenAI Python 라이브러리**
  - 요약 요청 로직 커스터마이징 (분할 요약, 간격별 요약 처리)

- **FastAPI**
  - Python 기반 파일 업로드 및 요약 결과 반환 API 서버로 활용
  - CORS 설정 및 비동기 처리 구조 설계

- **Spring Boot**
  - Java 기반 웹 백엔드 프레임워크
  - Thymeleaf 연동 및 REST API 설계에 사용

- **Thymeleaf + Thymeleaf Layout Dialect**
  - Spring Boot 템플릿 엔진
  - 페이지 구성 및 공통 레이아웃 처리에 활용

- **dotenv**
  - Python 환경에서 API 키 및 보안 환경변수 관리

- **Lombok**
  - Java 컴포넌트에서 반복되는 getter/setter, 생성자 코드 자동화
  - DTO 및 설정 클래스 간결화에 활용

※ 추가 수정사항 발생 시, 별도로 상세 기록 예정


---

