"""Basic JSON-based signup and login for the class project."""

import json
from pathlib import Path

import bcrypt

from models import Member


class AuthService:
    def __init__(self, file_path="users.json"):
        self.file_path = Path(file_path)

    def _read_users(self):
        if not self.file_path.exists():
            return {}
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_users(self, users):
        self.file_path.write_text(
            json.dumps(users, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def register(self, username, email, password):
        username = username.strip()
        email = email.strip().lower()

        if not username or not email or not password:
            return False, "모든 항목을 입력해 주세요.", None
        if "@" not in email:
            return False, "이메일 주소를 확인해 주세요.", None
        if len(password) < 6:
            return False, "비밀번호는 6자 이상으로 입력해 주세요.", None

        users = self._read_users()
        if username in users:
            return False, "이미 사용 중인 아이디입니다.", None
        if any(user.get("email", "").lower() == email for user in users.values()):
            return False, "이미 가입된 이메일입니다.", None

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        users[username] = {"email": email, "password_hash": password_hash}
        self._write_users(users)
        return True, "회원가입이 완료됐습니다.", Member(username, email)

    def login(self, username, password):
        username = username.strip()
        user_data = self._read_users().get(username)
        if not user_data or not password:
            return None

        try:
            password_matches = bcrypt.checkpw(
                password.encode("utf-8"),
                user_data["password_hash"].encode("utf-8"),
            )
        except (KeyError, ValueError):
            return None

        if password_matches:
            return Member(username, user_data["email"])
        return None
