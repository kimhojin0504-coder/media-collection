import os

import streamlit as st
from dotenv import load_dotenv

from auth import AuthService
from clients import TMDBClient, Yes24Client
from library import Library
from models import Guest


load_dotenv()
st.set_page_config(page_title="미디어 컬렉션", page_icon="🎬", layout="wide")
auth = AuthService()
library = Library()


def login_screen():
    st.title("🎬 미디어 컬렉션")
    st.caption("로그인하거나 게스트로 둘러보세요.")
    login_tab, signup_tab = st.tabs(["로그인", "회원가입"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("아이디")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", use_container_width=True)
        if submitted:
            user = auth.login(username, password)
            if user:
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호를 확인해 주세요.")

    with signup_tab:
        with st.form("signup_form"):
            new_username = st.text_input("아이디", key="signup_username")
            email = st.text_input("이메일", key="signup_email")
            new_password = st.text_input("비밀번호 (6자 이상)", type="password", key="signup_password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            submitted = st.form_submit_button("회원가입", use_container_width=True)
        if submitted:
            if new_password != confirm_password:
                st.error("비밀번호가 서로 다릅니다.")
            else:
                success, message, user = auth.register(new_username, email, new_password)
                if success:
                    st.session_state.current_user = user
                    st.rerun()
                else:
                    st.error(message)

    st.divider()
    if st.button("게스트로 둘러보기", use_container_width=True):
        st.session_state.current_user = Guest()
        st.rerun()


def show_site_rating(media):
    source = "YES24" if media.__class__.__name__ == "Book" else "TMDB"
    rating = media.site_rating
    if rating is None:
        st.caption(f"{source} 평점: 아직 없음")
        return
    st.markdown(f"**{source} 평점: {rating:.1f} / 10**")
    if media.rating_count:
        st.caption(f"평가 {media.rating_count:,}개")


def show_card(media, user, section):
    media_key = f"{media.__class__.__name__.lower()}_{media.media_id or media.title}"
    with st.container(border=True):
        image_col, info_col = st.columns([1, 4])
        with image_col:
            if media.poster_url:
                st.image(media.poster_url, use_container_width=True)
        with info_col:
            st.markdown(f"**{media.title}**")
            show_site_rating(media)
            st.caption(media.summary())
            detail_col, favorite_col = st.columns([1, 1])
            with detail_col:
                if st.button("상세 보기", key=f"detail_{section}_{media_key}"):
                    st.session_state.selected_media = media
                    st.rerun()
            with favorite_col:
                if user.can_favorite():
                    if st.button("찜하기", key=f"fav_{section}_{media_key}"):
                        library.add_favorite(user.username, media)
                        st.success("찜 목록에 저장했어요.")
                else:
                    st.button("찜하기", key=f"guest_fav_{section}_{media_key}", disabled=True)


def show_detail(media, user):
    if st.button("← 목록으로"):
        st.session_state.selected_media = None
        st.rerun()

    st.header(media.title)
    poster_col, detail_col = st.columns([1, 3])
    with poster_col:
        if media.poster_url:
            st.image(media.poster_url, use_container_width=True)
    with detail_col:
        show_site_rating(media)
        st.write(media.summary())
        if media.external_url:
            st.link_button("YES24 상품 페이지 열기", media.external_url)

        if user.can_rate():
            st.divider()
            st.subheader("내 평점")
            rating_key = f"{media.__class__.__name__.lower()}:{media.media_id}"
            saved_rating = library.get_user_data(user.username).get("ratings", {}).get(rating_key, {})
            rating = st.select_slider(
                "1점부터 5점까지 선택하세요",
                options=[1, 2, 3, 4, 5],
                value=saved_rating.get("rating", 5),
                key=f"detail_rating_{rating_key}",
            )
            if st.button("내 평점 저장", key=f"detail_save_{rating_key}"):
                library.set_rating(user.username, media, rating)
                st.success("평점을 저장했어요.")
            if st.button("찜하기", key=f"detail_favorite_{rating_key}"):
                library.add_favorite(user.username, media)
                st.success("찜 목록에 저장했어요.")
        else:
            st.info("회원으로 로그인하면 이 작품에 평점을 남기고 찜할 수 있어요.")


def show_activity(user):
    st.header("내 활동")
    activity = library.get_user_data(user.username)
    st.subheader("찜 목록")
    favorites = activity.get("favorites", [])
    if favorites:
        for item in favorites:
            st.write(f"**{item.get('title', '제목 없음')}** · {item.get('media_type', '')}")
    else:
        st.caption("아직 찜한 작품이 없습니다.")
    st.subheader("내 평점")
    ratings = activity.get("ratings", {})
    if ratings:
        for item in ratings.values():
            st.write(f"**{item.get('title', '제목 없음')}** · {item.get('rating', '-')}점")
    else:
        st.caption("아직 저장한 평점이 없습니다.")


def show_results(items, user, section):
    if items:
        for item in items[:10]:
            show_card(item, user, section)
    else:
        st.caption("검색 결과가 없습니다.")


if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "selected_media" not in st.session_state:
    st.session_state.selected_media = None

if st.session_state.current_user is None:
    login_screen()
    st.stop()

user = st.session_state.current_user
st.title("🎬 미디어 컬렉션")
st.caption("영화, 드라마, 도서를 찾아보고 나만의 컬렉션을 만들어 보세요.")
tmdb_key = os.getenv("TMDB_API_KEY", "")
yes24_key = os.getenv("YES24_API_KEY", "")
tmdb = TMDBClient(tmdb_key)
yes24 = Yes24Client(yes24_key)

with st.sidebar:
    st.write(f"사용자: **{user.username}**")
    if not user.can_favorite():
        st.caption("게스트 모드 · 찜과 평점은 로그인 후 이용 가능")
    page = st.radio("메뉴", ["메인", "내 활동"])
    if st.button("로그아웃"):
        st.session_state.current_user = None
        st.session_state.selected_media = None
        st.rerun()

selected_media = st.session_state.selected_media
if selected_media is not None:
    show_detail(selected_media, user)
    st.stop()

if page == "내 활동":
    if user.can_favorite():
        show_activity(user)
    else:
        st.header("내 활동")
        st.info("찜 목록과 평점을 보려면 로그인해 주세요.")
else:
    query = st.text_input("통합 검색", placeholder="영화, 드라마, 도서 제목을 검색하세요")
    if query:
        st.subheader(f"'{query}' 검색 결과")
        left, right = st.columns(2)
        with left:
            st.markdown("#### 영화 · 드라마")
            try:
                show_results(tmdb.search(query), user, "tmdb_search")
            except Exception as error:
                st.error(f"TMDB 검색 중 오류: {error}")
        with right:
            st.markdown("#### 도서")
            try:
                show_results(yes24.search(query), user, "yes24_search")
            except Exception as error:
                st.error(f"YES24 검색 중 오류: {error}")
    else:
        books_tab, series_tab, movies_tab = st.tabs(["인기 도서", "인기 드라마", "인기 영화"])
        with books_tab:
            st.subheader("YES24 베스트셀러")
            if yes24_key:
                try:
                    show_results(yes24.get_popular(), user, "yes24_popular")
                except Exception as error:
                    st.warning(f"YES24 API 응답을 확인해 주세요: {error}")
            else:
                st.info("YES24_API_KEY를 설정하면 베스트셀러를 불러옵니다.")

        with series_tab:
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
                    show_results(items, user, f"series_{choice}")
                except Exception as error:
                    st.error(f"TMDB API 오류: {error}")
            else:
                st.info("TMDB_API_KEY를 설정하면 드라마 목록을 불러옵니다.")

        with movies_tab:
            choice = st.radio("영화 목록", ["인기", "이달의", "급상승"], horizontal=True, label_visibility="collapsed")
            st.subheader(f"{choice} 영화")
            if tmdb_key:
                try:
                    if choice == "급상승":
                        items = tmdb.get_trending_movies()
                    elif choice == "이달의":
                        items = tmdb.get_movies_this_month()
                    else:
                        items = tmdb.get_popular("movie")
                    show_results(items, user, f"movies_{choice}")
                except Exception as error:
                    st.error(f"TMDB API 오류: {error}")
            else:
                st.info("TMDB_API_KEY를 설정하면 영화 목록을 불러옵니다.")
