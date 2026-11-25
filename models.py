"""Simple media classes used by the collection app."""


class Media:
    def __init__(self, title, overview="", poster_url="", media_id=""):
        self.title = title
        self.overview = overview
        self.poster_url = poster_url
        self.media_id = str(media_id)

    def summary(self):
        return self.overview or "소개가 아직 없습니다."

    def to_dict(self):
        return {
            "title": self.title,
            "overview": self.overview,
            "poster_url": self.poster_url,
            "media_id": self.media_id,
            "media_type": self.__class__.__name__.lower(),
        }


class Movie(Media):
    def __init__(self, title, overview="", poster_url="", media_id="", runtime=None):
        super().__init__(title, overview, poster_url, media_id)
        self.runtime = runtime

    def summary(self):
        text = super().summary()
        return f"{text}\n러닝타임: {self.runtime}분" if self.runtime else text


class Series(Media):
    def __init__(self, title, overview="", poster_url="", media_id="", seasons=None, episodes=None):
        super().__init__(title, overview, poster_url, media_id)
        self.seasons = seasons
        self.episodes = episodes

    def summary(self):
        text = super().summary()
        details = []
        if self.seasons is not None:
            details.append(f"시즌 {self.seasons}개")
        if self.episodes is not None:
            details.append(f"에피소드 {self.episodes}개")
        return f"{text}\n{' · '.join(details)}" if details else text


class Book(Media):
    def __init__(self, title, overview="", poster_url="", media_id="", author="", publisher="", isbn=""):
        super().__init__(title, overview, poster_url, media_id)
        self.author = author
        self.publisher = publisher
        self.isbn = isbn

    def summary(self):
        text = super().summary()
        details = " · ".join(value for value in (self.author, self.publisher) if value)
        return f"{text}\n{details}" if details else text


class User:
    """Base user class. Guests can browse but cannot save activity."""

    def __init__(self, username):
        self.username = username

    def can_favorite(self):
        return False

    def can_rate(self):
        return False


class Member(User):
    def __init__(self, username, email):
        super().__init__(username)
        self.email = email

    def can_favorite(self):
        return True

    def can_rate(self):
        return True


class Guest(User):
    def __init__(self):
        super().__init__("게스트")
