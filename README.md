# 미디어 컬렉션

Streamlit으로 만드는 영화·드라마·도서 컬렉션 프로젝트의 시작 파일입니다. API 키가 없어도 첫 화면은 실행됩니다.

## 실행 방법 (Windows PowerShell)

```powershell
cd outputs\media-library
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

API를 연결하려면 `.env` 파일을 열어 `TMDB_API_KEY`와 `YES24_API_KEY`에 발급받은 키를 입력하고 앱을 새로고침하세요. `.env`는 Git에 올리지 않도록 설정되어 있습니다.

YES24 API의 실제 응답 필드와 인증 정책은 아직 확인 전입니다. 응답 구조를 받은 뒤 `clients.py`의 `Yes24Client._get_books()` 필드 매핑을 맞춰 주세요.

현재 들어 있는 기능은 기본 Streamlit 화면, TMDB 영화·드라마 조회와 검색, YES24 도서 조회의 시작 구조, 미디어 클래스 상속, JSON 기반 찜·평점 저장용 클래스입니다. 로그인, 회원가입, 이메일 인증 UI는 이후 단계에서 붙일 수 있습니다.
