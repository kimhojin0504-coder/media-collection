"""A tiny JSON-backed store for favorites and ratings."""

import json
from pathlib import Path


class Library:
    def __init__(self, file_path="library.json"):
        self.file_path = Path(file_path)

    def _read(self):
        if not self.file_path.exists():
            return {}
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write(self, data):
        self.file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_user_data(self, username):
        data = self._read()
        return data.get(username, {"favorites": [], "ratings": {}})

    def add_favorite(self, username, media):
        data = self._read()
        user_data = data.setdefault(username, {"favorites": [], "ratings": {}})
        media_data = media.to_dict()
        existing = {
            (item.get("media_type"), str(item.get("media_id")))
            for item in user_data["favorites"]
        }
        media_key = (media_data["media_type"], str(media_data["media_id"]))
        if media_key not in existing:
            user_data["favorites"].append(media_data)
        self._write(data)

    def set_rating(self, username, media, rating):
        data = self._read()
        user_data = data.setdefault(username, {"favorites": [], "ratings": {}})
        user_data["ratings"][f"{media.__class__.__name__.lower()}:{media.media_id}"] = {
            "title": media.title,
            "rating": int(rating),
        }
        self._write(data)
