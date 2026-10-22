import datetime as dt
from zoneinfo import ZoneInfo

import requests
import streamlit as st

st.set_page_config(
    page_title="일출 · 일몰 · 낮 길이",
    page_icon="🌅",
    layout="centered",
)

API_URL = "https://api.sunrise-sunset.org/v2"
KST = ZoneInfo("Asia/Seoul")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
.stApp {
    background: linear-gradient(180deg, #fff4df 0%, #fffaf2 48%, #eef6ff 100%);
    color: #433d38;
    font-family: 'Noto Sans KR', sans-serif;
}
.block-container { max-width: 900px; padding-top: 2rem; padding-bottom: 3rem; }
.hero {
    padding: 1.6rem 1.2rem; text-align: center; border-radius: 26px;
    background: linear-gradient(130deg, #ffcc83, #ffe9b9 55%, #d8eaff);
    border: 1px solid rgba(255,255,255,.9);
    box-shadow: 0 8px 24px rgba(117, 94, 57, .12);
    margin-bottom: 1.2rem;
}
.hero h1 { font-size: clamp(1.9rem, 5vw, 3rem); font-weight: 900; color: #5b4634; margin: 0; }
.hero p { margin: .65rem 0 0; font-size: 1.05rem; color: #6d5949; }
.section-title { font-size: 1.3rem; font-weight: 900; margin: 1.2rem 0 .6rem; }
div[data-testid="stMetric"] {
    background: rgba(255,255,255,.82); border: 1px solid #f1dfc4;
    border-radius: 18px; padding: 1rem;
}
div[data-testid="stMetricLabel"] { font-weight: 700; }
.info-card {
    background: rgba(255,255,255,.82); border: 1px solid #eadcc8;
    border-radius: 18px; padding: 1rem 1.1rem; margin: .45rem 0;
}
.source { text-align: center; font-size: .9rem; color: #766b60; margin-top: 1.4rem; }
div.stButton > button { border-radius: 12px; font-weight: 700; min-height: 2.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🌅 일출 · 일몰 · 낮 길이</h1>
  <p>지구 어디에서든 날짜와 좌표를 선택해 태양의 하루를 확인해 보세요.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📍 1. 위치와 날짜 설정</div>', unsafe_allow_html=True)
with st.form("sun_form"):
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("위도 (°)", min_value=-90.0, max_value=90.0, value=37.5665, step=0.1, format="%.4f",
                              help="북위는 양수, 남위는 음수입니다. 서울 예시: 37.5665")
    with col2:
        lng = st.number_input("경도 (°)", min_value=-180.0, max_value=180.0, value=126.9780, step=0.1, format="%.4f",
                              help="동경은 양수, 서경은 음수입니다. 서울 예시: 126.9780")
    date_value = st.date_input("날짜", value=dt.datetime.now(KST).date())
    timezone_choice = st.selectbox(
        "표시 시간대",
        options=["좌표 위치의 현지 시간", "한국 표준시 (KST)", "UTC"],
        index=0,
        help="좌표 위치의 현지 시간은 API가 좌표를 바탕으로 시간대를 판단합니다.",
    )
    submitted = st.form_submit_button("☀️ 일출·일몰 정보 조회", use_container_width=True, type="primary")

if "sun_query" not in st.session_state:
    st.session_state.sun_query = None
if submitted:
    st.session_state.sun_query = {
        "lat": float(lat),
        "lng": float(lng),
        "date": date_value.isoformat(),
        "timezone_choice": timezone_choice,
    }

def parse_time(value):
    if value is None:
        return None
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed

def display_time(value, tz_choice):
    parsed = parse_time(value)
    if parsed is None:
        return "해당 날짜에 발생하지 않음"
    if tz_choice == "한국 표준시 (KST)":
