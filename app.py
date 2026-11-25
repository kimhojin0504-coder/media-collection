import os

import streamlit as st
from dotenv import load_dotenv

from clients import TMDBClient, Yes24Client
from library import Library


load_dotenv()
st.set_page_config(page_title="미디어 컬렉션", page_icon="🎬", layout="wide")
st.title("🎬 미디어 컬렉션")
st.caption("영화, 드라마, 도서를 찾아보고 나만의 컬렉션을 만들어 보세요.")

tmdb_key = os.getenv("TMDB_API_KEY", "")
yes24_key = os.getenv("YES24_API_KEY", "")
tmdb = TMDBClient(tmdb_key)
yes24 = Yes24Client(yes24_key)
library = Library()

if "username" not in st.session_state:
    st.session_state.username = "guest"
if "page" not in st.session_state:
    st.session_state.page = "메인"

with st.sidebar:
    st.subheader("메뉴")
    page = st.radio("화면", ["메인", "내 활동"], label_visibility="collapsed")
    st.session_state.page = page
    st.caption("현재는 게스트 미리보기입니다. 로그인 기능은 다음 단계에서 추가합니다.")

if page == "내 활동":
    st.header("내 활동")
    st.info("찜과 평점 기능은 다음 단계에서 연결할 예정입니다.")
else:
    query = st.text_input("통합 검색", placeholder="영화, 드라마, 도서 제목을 검색하세요")
    if query:
        st.subheader(f"'{query}' 검색 결과")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 영화 · 드라마")
            try:
                results = tmdb.search(query)
                if results:
                    for media in results[:10]:
                        with st.container(border=True):
                            st.write(f"**{media.title}**")
                            st.caption(media.summary())
                else:
                    st.caption("결과가 없거나 TMDB 키가 설정되지 않았습니다.")
            except Exception as error:
                st.error(f"TMDB 검색 중 오류: {error}")
        with col2:
            st.markdown("#### 도서")
            try:
                books = yes24.search(query)
                if books:
                    for book in books[:10]:
                        st.write(f"**{book.title}**")
                        st.caption(book.summary())
                else:
                    st.caption("결과가 없거나 YES24 키가 설정되지 않았습니다.")
            except Exception as error:
                st.error(f"YES24 검색 중 오류: {error}")
    else:
        tab_books, tab_series, tab_movies = st.tabs(["인기 도서", "인기 드라마", "인기 영화"])
        with tab_books:
            st.subheader("YES24 베스트셀러")
            if yes24_key:
                try:
                    for book in yes24.get_popular()[:10]:
                        st.write(f"**{book.title}**")
                        st.caption(book.summary())
                except Exception as error:
                    st.warning(f"YES24 API 응답을 확인해 주세요: {error}")
            else:
                st.info("YES24_API_KEY를 .env에 설정하면 베스트셀러를 불러옵니다.")
        with tab_series:
            choice = st.radio("드라마 목록", ["인기", "이달의", "급상승"], horizontal=True, label_visibility="collapsed")
            st.subheader(f"{choice} 드라마")
            if tmdb_key:
                try:
                    if choice == "급상승":
                        items = tmdb.get_trending_series()
                    elif choice == "이달의":
                        items = tmdb.get_series_this_month()
                    else:
                        items = tmdb.get_popular("tv")
                    for item in items[:10]:
                        st.write(f"**{item.title}**")
                        st.caption(item.summary())
                except Exception as error:
                    st.error(f"TMDB API 오류: {error}")
            else:
                st.info("TMDB_API_KEY를 .env에 설정하면 드라마 목록을 불러옵니다.")
        with tab_movies:
            st.subheader("인기 영화")
            if tmdb_key:
                try:
                    for movie in tmdb.get_popular("movie")[:10]:
                        st.write(f"**{movie.title}**")
                        st.caption(movie.summary())
                except Exception as error:
                    st.error(f"TMDB API 오류: {error}")
            else:
                st.info("TMDB_API_KEY를 .env에 설정하면 인기 영화를 불러옵니다.")
