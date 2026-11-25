"""Small API clients. YES24 response mapping can be adjusted after testing its API."""

import requests
import streamlit as st

from models import Book, Movie, Series


class BaseClient:
    def search(self, query):
        raise NotImplementedError

    def get_popular(self):
        raise NotImplementedError


class TMDBClient(BaseClient):
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_URL = "https://image.tmdb.org/t/p/w500"

    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, path, params=None):
        if not self.api_key:
            return {}
        request_params = {"api_key": self.api_key, "language": "ko-KR"}
        request_params.update(params or {})
        response = requests.get(f"{self.BASE_URL}{path}", params=request_params, timeout=15)
        response.raise_for_status()
        return response.json()

    def _make_media(self, item, media_type):
        poster = item.get("poster_path")
        poster_url = f"{self.IMAGE_URL}{poster}" if poster else ""
        rating = item.get("vote_average")
        rating = rating if rating and rating > 0 else None
        rating_count = item.get("vote_count")
        if media_type == "movie":
            return Movie(
                item.get("title", "제목 없음"), item.get("overview", ""),
                poster_url, item.get("id"), site_rating=rating, rating_count=rating_count,
            )
        return Series(
            item.get("name", "제목 없음"), item.get("overview", ""),
            poster_url, item.get("id"), site_rating=rating, rating_count=rating_count,
        )

    def get_popular(self, media_type="movie"):
        result = self._get(f"/{media_type}/popular")
        return [self._make_media(item, media_type) for item in result.get("results", [])]

    def get_trending_series(self):
        result = self._get("/trending/tv/week")
        return [self._make_media(item, "tv") for item in result.get("results", [])]

    def get_trending_movies(self):
        result = self._get("/trending/movie/week")
        return [self._make_media(item, "movie") for item in result.get("results", [])]

    def get_series_this_month(self):
        from datetime import date

        today = date.today()
        first_day = today.replace(day=1).isoformat()
        result = self._get("/discover/tv", {"first_air_date.gte": first_day, "first_air_date.lte": today.isoformat(), "sort_by": "popularity.desc"})
        return [self._make_media(item, "tv") for item in result.get("results", [])]

    def get_movies_this_month(self):
        from calendar import monthrange
        from datetime import date

        today = date.today()
        first_day = today.replace(day=1).isoformat()
        last_day = today.replace(day=monthrange(today.year, today.month)[1]).isoformat()
        result = self._get("/discover/movie", {
            "primary_release_date.gte": first_day,
            "primary_release_date.lte": last_day,
            "sort_by": "popularity.desc",
            "region": "KR",
        })
        return [self._make_media(item, "movie") for item in result.get("results", [])]

    def search(self, query):
        results = []
        for media_type in ("movie", "tv"):
            data = self._get(f"/search/{media_type}", {"query": query})
            results.extend(self._make_media(item, media_type) for item in data.get("results", []))
        return results


class Yes24Client(BaseClient):
    BASE_URL = "https://apis.yes24.com"

    def __init__(self, api_key):
        self.api_key = api_key

    def _get_books(self, path, params=None):
        if not self.api_key:
            return []
        response = requests.get(
            f"{self.BASE_URL}{path}",
            headers={"X-Api-Key": self.api_key},
            params=params or {},
            timeout=15,
        )
        response.raise_for_status()
        response_data = response.json().get("data", {})
        items = response_data.get("items", [])
        books = []
        for item in items:
            content = item.get("contentDetail") or {}
            books.append(Book(
                title=item.get("title", "제목 없음"),
                overview=content.get("bookIntroduction") or content.get("bookSummary") or "",
                poster_url=item.get("cover", ""),
                media_id=item.get("itemId", item.get("isbn13", "")),
                author=item.get("author", ""),
                publisher=item.get("publisher", ""),
                isbn=item.get("isbn13", item.get("isbn10", "")),
                site_rating=item.get("starScore"),
                external_url=item.get("link", ""),
            ))
        return books

    def get_popular(self):
        return self._get_books("/v1/category/bestseller", {"categoryId": "001", "detail": "Y"})

    def search(self, query):
        return self._get_books("/v1/goods/itemList", {"query": query, "detail": "Y"})
