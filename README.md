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

현재 기능에는 TMDB 영화·드라마와 YES24 도서 조회·검색, 회원가입·로그인·게스트 둘러보기, 회원 전용 찜·평점, 내 활동 화면이 포함됩니다. 회원 정보는 `users.json`, 찜과 평점은 `library.json`에 저장됩니다. 두 JSON 파일과 `.env`는 GitHub에 올리지 않도록 `.gitignore`에 등록되어 있습니다.

회원가입은 현재 이메일 코드 인증 없이 동작합니다. 이메일 인증과 아이디·비밀번호 찾기는 다음 단계에서 추가할 수 있습니다.

영화 탭에는 인기·이달의·급상승 목록이 있습니다. 작품 카드에서 상세 화면을 열면 TMDB 또는 YES24의 사이트 평점과 회원 개인 평점을 확인하거나 저장할 수 있습니다. 기본 화면은 다크 테마이며, Streamlit 오른쪽 위 메뉴에서 라이트/다크 테마를 바꿀 수 있습니다.
