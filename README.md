
# Defense Analysis Console — Streamlit (Prototype v0.1)

해군 분석관 좌담회(2022‑10‑13) 기반 인사이트를 반영한 저충실도 통합 UI 프로토타입입니다.  
엑셀 원본(`interview 221013`)을 업로드하거나 `data/sample_long.csv` 샘플로 즉시 실행할 수 있습니다.

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```
- 브라우저에서 `http://localhost:8501` 자동 오픈
- 좌측 사이드바에서 엑셀 업로드 또는 샘플 사용 선택

## 폴더 구조
```
.
├─ app.py                 # Streamlit 메인 앱
├─ requirements.txt       # 의존성
├─ data/
│  └─ sample_long.csv     # 샘플 데이터(롱포맷)
└─ README.md
```

## 기능(개념 시연)
- **맥락 동시가시**: 좌(과제/메타/보안) ‑ 중(시나리오/Run Profile) ‑ 우(결과/미니상황도)
- **부분참조 vs 스냅샷**: 시나리오 블록의 재사용 패턴 구분(버튼 토스트로 개념 시연)
- **Run Profile Δ 비교**: 변수 차이/민감도 하이라이트(스텁)
- **보고서 마법사**: 보안등급/템플릿/자동요약(스텁)
- **감사추적**: Who/When/Why 로그(스텁)
- **인터뷰 데이터 탐색**: 필터/표/문제키워드 빈도(필터 반영)

## GitHub 업로드
```bash
git init
git add .
git commit -m "Init: Defense Analysis Console — Streamlit v0.1"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```
※ `<YOUR_GITHUB_REPO_URL>`에 본인 저장소 URL을 넣으세요.

## Streamlit Cloud 배포(선택)
1. 새 GitHub 리포지토리 연결
2. Deploy → Main branch → `app.py` 지정

## 데이터 소스
- `interview 221013` 형식의 엑셀을 업로드하면 자동 파싱하여 롱포맷으로 변환
- 샘플: `data/sample_long.csv`(이 리포에 포함)
