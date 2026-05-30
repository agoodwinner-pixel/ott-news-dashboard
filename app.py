import streamlit as st
import pandas as pd
import requests
import urllib.request
import urllib.parse
import urllib.error
import json
import re
import ssl
import time
import difflib
import concurrent.futures
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import email.utils
import random
import math
import os

# ==========================================
# 1. 디자인 및 페이지 설정 (다크 테마)
# ==========================================
st.set_page_config(page_title="Strategic Intelligence Dashboard", page_icon="📡", layout="wide")

ssl._create_default_https_context = ssl._create_unverified_context
KST = timezone(timedelta(hours=9))

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp {
        background: linear-gradient(160deg, #f8f9fc 0%, #eef1f8 40%, #f3f0ff 70%, #f8f9fc 100%);
        color: #1e293b;
        font-family: 'Inter', sans-serif;
    }
    .header-box {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 50%, #ede9fe 100%);
        padding: 6px 16px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title {
        color: #0f172a;
        font-size: 13px;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .header-subtitle { display: none; }
    [data-testid="stMetric"] {
        background: #ffffff;
        padding: 18px 22px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricLabel"] { color: #64748b !important; font-weight: 600; letter-spacing: 0.5px; }
    [data-testid="stMetricValue"] { color: #1e293b !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background: #ffffff;
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        border: 1px solid #e2e8f0;
        border-bottom: none;
        color: #64748b;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.2);
    }
    .stDataFrame {
        background: #ffffff;
        border-radius: 12px;
        padding: 12px;
        border: 1px solid #e2e8f0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        height: 48px;
        font-weight: 700;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99,102,241,0.2);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        box-shadow: 0 6px 20px rgba(99,102,241,0.35);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fc 0%, #f1f5f9 50%, #ede9fe 100%);
        border-right: 1px solid #e2e8f0;
    }
    .news-card {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        height: 100%;
    }
    .news-card:hover {
        box-shadow: 0 8px 24px rgba(99,102,241,0.12);
        transform: translateY(-2px);
    }
    .news-card img {
        width: 100%;
        height: 140px;
        object-fit: cover;
    }
    .news-card .card-body {
        padding: 14px 16px;
    }
    .news-card .card-date {
        font-size: 11px;
        color: #94a3b8;
        margin-bottom: 6px;
        font-weight: 500;
    }
    .news-card .card-title {
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
        line-height: 1.4;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-card .card-desc {
        font-size: 12px;
        color: #64748b;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    .news-card .card-tag {
        display: inline-block;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        margin-top: 8px;
    }
    .tag-core { background: #ede9fe; color: #7c3aed; }
    .tag-normal { background: #e0f2fe; color: #0284c7; }
    .tag-rescued { background: #fef3c7; color: #d97706; }
    .mini-stat {
        display: inline-block;
        background: #f8f9fc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px 14px;
        margin-right: 8px;
        font-size: 12px;
        color: #64748b;
    }
    .mini-stat b { color: #1e293b; font-size: 16px; }
    /* KT 그룹사 토글 칩 — kt-chips 내부만 */
    .kt-chips [data-testid="stHorizontalBlock"] .stButton>button {
        font-size: 10px !important;
        padding: 2px 4px !important;
        height: 28px !important;
        min-height: 28px !important;
        border-radius: 6px !important;
        white-space: nowrap !important;
    }
    .kt-chips [data-testid="stHorizontalBlock"] .stButton>button[kind="primary"],
    .kt-chips [data-testid="stHorizontalBlock"] .stButton>button[data-testid="stBaseButton-primary"] {
        background: #4f46e5 !important;
        color: #ffffff !important;
        border: 2px solid #4f46e5 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(79,70,229,0.3) !important;
    }
    .kt-chips [data-testid="stHorizontalBlock"] .stButton>button[kind="secondary"],
    .kt-chips [data-testid="stHorizontalBlock"] .stButton>button[data-testid="stBaseButton-secondary"] {
        background: #f1f5f9 !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
    }
    /* 다크 다이얼 패널 — 좌측 컬럼 전체 배경 */
    .dark-dial {
        background: linear-gradient(160deg, #18163a 0%, #1e1b4b 40%, #252262 100%);
        border-radius: 20px;
        padding: 24px 20px 8px;
        margin-bottom: -16px;
    }
    .dial-col [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(160deg, #18163a 0%, #1e1b4b 40%, #252262 100%);
        border-radius: 20px;
        padding: 0 16px 16px;
    }
    .dial-col [data-testid="stHorizontalBlock"] .stButton>button {
        background: rgba(255,255,255,0.06) !important;
        border: 1.5px solid rgba(255,255,255,0.10) !important;
        border-radius: 12px !important;
        color: #c7d2fe !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 8px 2px !important;
        height: 38px !important;
        min-height: 38px !important;
        white-space: nowrap !important;
        line-height: 1.2 !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }
    .dial-col [data-testid="stHorizontalBlock"] .stButton>button:hover {
        background: rgba(99,102,241,0.25) !important;
        border-color: #818cf8 !important;
    }
    .dial-col [data-testid="stHorizontalBlock"] .stButton>button[kind="primary"],
    .dial-col [data-testid="stHorizontalBlock"] .stButton>button[data-testid="stBaseButton-primary"] {
        background: rgba(99,102,241,0.35) !important;
        border-color: #818cf8 !important;
        color: #fff !important;
        box-shadow: 0 0 16px rgba(99,102,241,0.3) !important;
    }
    /* 추천 메인 버튼 */
    .dial-col .stButton>button[data-testid="stBaseButton-primary"] {
        font-size: 15px !important;
        font-weight: 700 !important;
        min-height: 62px !important;
        height: 62px !important;
        border-radius: 14px !important;
        padding: 16px !important;
        background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%) !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
        white-space: normal !important;
    }
    /* 룰렛 서브 버튼 */
    .dial-col .stButton>button[data-testid="stBaseButton-secondary"] {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #c7d2fe !important;
        border-radius: 14px !important;
        min-height: 52px !important;
        height: 52px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        white-space: normal !important;
    }
    /* 룰렛 애니메이션 */
    @keyframes spin-slot {
        0% { transform: translateY(0); }
        100% { transform: translateY(-100%); }
    }
    .roulette-window {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
        border-radius: 20px;
        padding: 32px;
        text-align: center;
        margin: 12px 0;
        box-shadow: 0 12px 40px rgba(67,56,202,0.3);
        overflow: hidden;
        position: relative;
    }
    .roulette-window::before, .roulette-window::after {
        content: '';
        position: absolute;
        left: 0; right: 0;
        height: 40px;
        z-index: 2;
        pointer-events: none;
    }
    .roulette-window::before { top: 0; background: linear-gradient(180deg, #1e1b4b, transparent); }
    .roulette-window::after { bottom: 0; background: linear-gradient(0deg, #1e1b4b, transparent); }
    .slot-track {
        display: inline-flex;
        flex-direction: column;
        animation: spin-slot 0.4s linear infinite;
    }
    .slot-item {
        font-size: 32px;
        font-weight: 800;
        color: #fff;
        padding: 10px 0;
        white-space: nowrap;
    }
    .roulette-result {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        border-radius: 20px;
        padding: 36px 24px;
        text-align: center;
        margin: 12px 0;
        box-shadow: 0 12px 40px rgba(99,102,241,0.3);
    }
    .result-emoji { font-size: 52px; }
    .result-menu {
        font-size: 36px;
        font-weight: 800;
        color: #fff;
        margin: 8px 0;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    .result-sub { font-size: 14px; color: #e0e7ff; }
    .rest-list-card {
        background: #fff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        display: flex;
        align-items: center;
        gap: 14px;
        transition: all 0.2s ease;
    }
    .rest-list-card:hover {
        box-shadow: 0 6px 20px rgba(99,102,241,0.12);
        transform: translateY(-1px);
    }
    .rest-rank {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff;
        font-weight: 800;
        font-size: 14px;
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .rest-info { flex: 1; min-width: 0; }
    .rest-name { font-size: 15px; font-weight: 700; color: #1e293b; }
    .rest-meta { font-size: 11px; color: #94a3b8; margin-top: 2px; }
    .rest-links { display: flex; gap: 8px; flex-shrink: 0; }
    .rest-links a {
        font-size: 11px;
        font-weight: 600;
        color: #6366f1;
        text-decoration: none;
        background: #eef2ff;
        padding: 4px 10px;
        border-radius: 8px;
        transition: background 0.2s;
    }
    .rest-links a:hover { background: #c7d2fe; }
    /* ===== 맛집 탭 — 다크 좌측 + 라이트 우측 ===== */
    .dial-panel {
        background: linear-gradient(160deg, #18163a 0%, #1e1b4b 40%, #252262 100%);
        border-radius: 20px;
        padding: 28px 24px;
        color: #e0e7ff;
        height: 100%;
    }
    .dial-title {
        font-size: 17px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 4px;
    }
    .dial-sub {
        font-size: 12px;
        color: #a5b4fc;
        margin-bottom: 20px;
    }
    .dial-label {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
        margin: 16px 0 8px;
    }
    /* 다크 패널 내부 Streamlit 버튼 오버라이드 */
    .dark-dial [data-testid="stHorizontalBlock"] .stButton>button {
        background: rgba(255,255,255,0.06) !important;
        border: 1.5px solid rgba(255,255,255,0.10) !important;
        border-radius: 14px !important;
        color: #c7d2fe !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 10px 6px !important;
        height: auto !important;
        min-height: 52px !important;
        white-space: pre-wrap !important;
        line-height: 1.3 !important;
        box-shadow: none !important;
    }
    .dark-dial [data-testid="stHorizontalBlock"] .stButton>button:hover {
        background: rgba(99,102,241,0.25) !important;
        border-color: #818cf8 !important;
    }
    .dark-dial [data-testid="stHorizontalBlock"] .stButton>button[kind="primary"],
    .dark-dial [data-testid="stHorizontalBlock"] .stButton>button[data-testid="stBaseButton-primary"] {
        background: rgba(99,102,241,0.35) !important;
        border-color: #818cf8 !important;
        color: #fff !important;
        box-shadow: 0 0 16px rgba(99,102,241,0.3) !important;
    }
    /* 추천 메인 버튼 (다크 패널) */
    .dark-dial > div[data-testid="stVerticalBlock"] > div:last-of-type .stButton>button,
    .dark-dial .big-action .stButton>button {
        font-size: 16px !important;
        font-weight: 700 !important;
        min-height: 60px !important;
        height: 60px !important;
        border-radius: 14px !important;
        padding: 16px !important;
    }
    /* 우측 결과 패널 */
    .result-panel {
        background: #f8f9fc;
        border-radius: 20px;
        padding: 28px 24px;
        border: 1px solid #e2e8f0;
        min-height: 480px;
    }
    .result-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .result-header-title {
        font-size: 17px;
        font-weight: 800;
        color: #1e293b;
    }
    .result-badge {
        font-size: 11px;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 4px 12px;
        color: #64748b;
        font-weight: 600;
    }
    .result-cat-tag {
        display: inline-block;
        background: #312e81;
        color: #e0e7ff;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .rest-top-name {
        font-size: 22px;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .rest-top-rating {
        color: #22c55e;
        font-size: 14px;
        font-weight: 700;
    }
    .rest-top-desc {
        font-size: 13px;
        color: #475569;
        line-height: 1.7;
        margin: 12px 0;
    }
    .rest-quote {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border-radius: 14px;
        padding: 20px;
        margin: 16px 0;
        position: relative;
    }
    .rest-quote-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #22c55e;
        color: #fff;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .rest-quote-text {
        font-size: 13px;
        color: #c7d2fe;
        line-height: 1.7;
        font-style: italic;
    }
    .rest-info-row {
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 13px;
    }
    .rest-info-icon {
        width: 28px;
        text-align: center;
        color: #6366f1;
        flex-shrink: 0;
    }
    .rest-info-label {
        color: #64748b;
        font-weight: 600;
        min-width: 80px;
    }
    .rest-info-value {
        color: #1e293b;
        font-weight: 500;
        flex: 1;
        text-align: right;
    }
    .rest-info-value.price {
        color: #6366f1;
        font-weight: 700;
    }
    .rest-tip-box {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 14px;
        padding: 18px;
        margin: 16px 0;
    }
    .rest-tip-title {
        font-size: 12px;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 6px;
    }
    .rest-tip-text {
        font-size: 12px;
        color: #475569;
        line-height: 1.7;
    }
    .food-action-btn {
        display: block;
        width: 100%;
        text-align: center;
        font-size: 15px;
        font-weight: 700;
        border: none;
        border-radius: 14px;
        padding: 16px;
        cursor: pointer;
        margin-bottom: 10px;
        transition: all 0.2s;
    }
    .food-action-primary {
        background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%);
        color: #fff;
        box-shadow: 0 4px 20px rgba(99,102,241,0.25);
    }
    .food-action-secondary {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <div>
        <h1 class="header-title">📡 S.I. Dashboard <span style="font-size:11px; background: linear-gradient(135deg, #6366f1, #8b5cf6); padding:3px 10px; border-radius:12px; font-weight:600; color:white;">V3.2</span></h1>
        <div class="header-subtitle">OTT 산업 동향 및 KT 그룹사 통합 뉴스 기사검색</div>
    </div>
    <div style="background: #f0fdf4; padding:6px 14px; border-radius:20px; border:1px solid #bbf7d0; font-size:12px; color:#16a34a;">
        ● Online
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. API 키 및 딕셔너리 설정
# ==========================================
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception:
    st.error("🚨 API 키를 Streamlit Cloud Secrets에 설정해주세요.")
    st.stop()

# --- [OTT 관련 필터링 사전] ---
_DEFAULT_BLACK = ["출연", "캐스팅", "첫방", "시청률", "아이돌", "배우", "드라마", "예능", "화제", "포토", "종영", "비하인드", "팬미팅", "제작발표회", "라인업", "시즌2", "결말", "티저", "감독", "예고편", "포스터", "신작", "몇부작", "연기", "정체", "시청자", "관전포인트", "스포일러", "안방극장", "스크린", "줄거리", "회차", "번개맨", "애니메이션", "공개", "스트리밍", "시청 가능", "시청하기", "시청할 수 있", "볼 수 있", "감상", "독점 공개", "론칭", "오리지널 시리즈", "오리지널 콘텐츠", "편성", "방영", "개봉", "방송되며"]
_DEFAULT_STRONG_WHITE = ["인수", "지분", "실적", "공정위", "구조조정", "적자", "흑자", "매출", "투자", "MAU", "점유율", "가입자", "기업결합", "시너지", "주주", "재무", "매각", "영업이익"]
_DEFAULT_NORMAL_WHITE = ["전략", "대표", "규제", "토종", "연합", "광고", "요금제", "영입", "플랫폼", "동향", "경쟁", "무료", "생존", "이용률", "출시", "생태계"]

_FILTER_FILE = os.path.join(os.path.dirname(__file__) or '.', 'ott_filters.json')

def _load_filters():
    if os.path.exists(_FILTER_FILE):
        with open(_FILTER_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"black": _DEFAULT_BLACK, "strong_white": _DEFAULT_STRONG_WHITE, "normal_white": _DEFAULT_NORMAL_WHITE}

def _save_filters(data):
    with open(_FILTER_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'ott_filters' not in st.session_state:
    st.session_state['ott_filters'] = _load_filters()

OTT_BLACK_LIST = st.session_state['ott_filters']['black']
OTT_STRONG_WHITE = st.session_state['ott_filters']['strong_white']
OTT_NORMAL_WHITE = st.session_state['ott_filters']['normal_white']

# --- [KT 관련 검색 및 필터링 사전] ---
KT_COMPANIES_MAP = {
    "KT/케이티": '"KT" | "케이티" | "Korea Telecom"',
    "스튜디오지니": '"KT스튜디오지니" | "스튜디오지니"',
    "KT ENA/ENA": '"KT ENA" | "ENA 채널" | "채널 ENA"',
    "스카이라이프": '"KT스카이라이프" | "케이티스카이라이프" | "스카이라이프"',
    "밀리의서재": '"밀리의서재" | "밀리의 서재"',
    "지니뮤직": '"지니뮤직" | "KT지니뮤직"',
    "나스미디어": '"나스미디어" | "KT나스미디어"',
    "HCN": '"KT HCN" | "케이티에이치씨엔" | "HCN방송"',
    "KT알파": '"KT알파" | "케이티알파" | "알파쇼핑"',
    "KT알티미디어": '"KT알티미디어" | "케이티알티미디어" | "KT Altimedia" | "알티미디어"'
}

KT_VALIDATION_KEYWORDS = {
    "KT/케이티": [r"(?<![A-Za-z])KT(?![A-Za-z&])", r"케이티", r"Korea\s*Telecom", r"주식회사\s*KT"],
    "스튜디오지니": [r"스튜디오지니", r"스튜디오\s*지니", r"KT\s*스튜디오지니"],
    "KT ENA/ENA": [r"KT\s*ENA", r"ENA\s*채널", r"채널\s*ENA", r"케이티\s*이엔에이"],
    "스카이라이프": [r"KT\s*스카이라이프", r"케이티\s*스카이라이프", r"스카이라이프"],
    "밀리의서재": [r"밀리의\s*서재"],
    "지니뮤직": [r"지니뮤직", r"지니\s*뮤직", r"KT\s*지니뮤직"],
    "나스미디어": [r"나스미디어", r"KT\s*나스미디어"],
    "HCN": [r"KT\s*HCN", r"에이치씨엔", r"HCN\s*방송", r"HCN"],
    "KT알파": [r"KT\s*알파", r"케이티\s*알파", r"알파\s*쇼핑"],
    "KT알티미디어": [r"KT\s*알티미디어", r"KT\s*Altimedia", r"알티미디어"]
}

KT_EXCLUSION_KEYWORDS = {
    "KT/케이티": [r"LCK", r"선거", r"투구", r"스포츠", r"WBC", r"신인왕", r"\[인사\]", r"선발", r"감독", r"우승", r"선두", r"포토", r"야구", r"프로야구", r"위즈", r"wiz", r"KBO", r"이강철", r"홈런", r"투수", r"타자", r"농구", r"프로농구", r"KBL", r"소닉붐", r"부산 KCC", r"허웅", r"허훈", r"농구단"]
}

# ==========================================
# 3. 공통 유틸리티 함수
# ==========================================
def clean_html(text):
    if not text: return ""
    text = re.sub(r'<.*?>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').strip()

def fetch_article_text(url):
    """기사 원문(Body)을 긁어오는 함수"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            return re.sub(r'\s+', ' ', soup.get_text(separator=' ')).strip()
    except Exception:
        return ""

def fetch_article_image(url):
    """기사 대표 이미지(og:image) 추출"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            soup = BeautifulSoup(response.read(), 'html.parser')
            og = soup.find('meta', property='og:image')
            if og and og.get('content'):
                return og['content']
    except Exception:
        pass
    return ""

def is_similar_title(new_title, existing_titles, threshold=0.7):
    """제목 중복 제거 함수"""
    clean_new = re.sub(r'[^가-힣a-zA-Z0-9]', '', new_title)
    for existing in existing_titles:
        clean_ext = re.sub(r'[^가-힣a-zA-Z0-9]', '', existing)
        if difflib.SequenceMatcher(None, clean_new, clean_ext).ratio() >= threshold:
            return True
    return False

# ==========================================
# 4. OTT 뉴스 분석 로직 (본문 검사 추가됨)
# ==========================================
def analyze_ott_news(title, description, link):
    combined_info = title + " " + description
    has_black = any(w in combined_info for w in OTT_BLACK_LIST)
    has_strong = any(w in combined_info for w in OTT_STRONG_WHITE)
    has_normal = any(w in combined_info for w in OTT_NORMAL_WHITE)
    
    # 1. 제목+요약 검사
    if has_strong: return True, ("⚡ 구출됨 (강력단어)" if has_black else "✅ 핵심 산업")
    if has_normal and not has_black: return True, "✅ 일반 산업"
    
    # 2. [신규 로직] 제목/요약에서 애매하면 본문을 긁어와서 재검사!
    if not has_black:
        body_text = fetch_article_text(link)
        if body_text:
            body_has_black = any(w in body_text for w in OTT_BLACK_LIST)
            if any(w in body_text for w in OTT_STRONG_WHITE) and not body_has_black:
                return True, "✅ 핵심 산업 (본문 감지)"
            if any(w in body_text for w in OTT_NORMAL_WHITE) and not body_has_black:
                return True, "✅ 일반 산업 (본문 감지)"
            if body_has_black:
                return False, "🚫 연예/홍보성 (본문 감지)"
    
    if has_black: return False, "🚫 연예/홍보성"
    return False, "🚫 산업 단어 없음"

def fetch_ott_news(query, limit_date):
    encoded_query = urllib.parse.quote(query)
    valid_list, filtered_list, saved_titles = [], [], []
    
    for start_idx in range(1, 402, 100):
        url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display=100&start={start_idx}&sort=date"
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", CLIENT_ID)
        req.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
        
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode('utf-8'))
                items = data.get('items', [])
                if not items: break
                
                for item in items:
                    dt = email.utils.parsedate_to_datetime(item['pubDate']).astimezone(KST)
                    if dt < limit_date:
                        return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)
                    
                    title = clean_html(item['title'])
                    if is_similar_title(title, saved_titles): continue
                    saved_titles.append(title)
                    
                    desc, link = clean_html(item['description']), item['link']
                    is_valid, reason = analyze_ott_news(title, desc, link)
                    
                    news_data = {"발행일": dt.strftime("%m-%d %H:%M"), "제목": title, "요약": desc, "기사링크": link, "분류": reason}
                    if is_valid: valid_list.append(news_data)
                    else: filtered_list.append(news_data)
        except Exception:
            break
            
    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)

# ==========================================
# 5. KT 그룹사 뉴스 분석 로직 (병렬 처리)
# ==========================================
def fetch_single_kt_news(company_name, query, limit_date):
    encoded_query = urllib.parse.quote(query)
    results, saved_titles = [], []
    
    for start_idx in range(1, 402, 100):
        url = f"https://openapi.naver.com/v1/search/news.json?query={encoded_query}&display=100&start={start_idx}&sort=date"
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", CLIENT_ID)
        req.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                items = data.get('items', [])
                if not items: break
                
                for item in items:
                    dt = email.utils.parsedate_to_datetime(item['pubDate']).astimezone(KST)
                    if dt < limit_date:
                        return company_name, results
                        
                    title = clean_html(item['title'])
                    if is_similar_title(title, saved_titles): continue
                    
                    desc, link = clean_html(item['description']), item['link']
                    combined_info = title + " " + desc
                    
                    # 1. 블랙리스트 검사 (스포츠 등)
                    exclusions = KT_EXCLUSION_KEYWORDS.get(company_name, [])
                    if any(re.search(p, combined_info, re.IGNORECASE) for p in exclusions):
                        continue
                        
                    article_data = {"그룹사명": company_name, "발행일": dt.strftime("%m-%d %H:%M"), "제목": title, "기사링크": link}
                    
                    # 2. 화이트리스트 검사 (제목+요약)
                    patterns = KT_VALIDATION_KEYWORDS.get(company_name, [])
                    is_valid = not patterns or any(re.search(p, combined_info, re.IGNORECASE) for p in patterns)
                    
                    # 3. 본문 검사
                    if not is_valid:
                        body_text = fetch_article_text(link)
                        is_valid = any(re.search(p, body_text, re.IGNORECASE) for p in patterns)
                        
                    if is_valid:
                        results.append(article_data)
                        saved_titles.append(title)
        except Exception:
            break
            
    return company_name, results

def fetch_all_kt_news(limit_date):
    all_news_data = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_single_kt_news, comp, q, limit_date): comp for comp, q in KT_COMPANIES_MAP.items()}
        for future in concurrent.futures.as_completed(futures):
            comp, news_list = future.result()
            all_news_data.extend(news_list)
            
    if all_news_data:
        df = pd.DataFrame(all_news_data)
        # 지정된 순서대로 정렬
        df['그룹사명'] = pd.Categorical(df['그룹사명'], categories=list(KT_COMPANIES_MAP.keys()), ordered=True)
        return df.sort_values(['그룹사명', '발행일'], ascending=[True, False])
    return pd.DataFrame()

# ==========================================
# 6. 광화문 맛집 추천 로직
# ==========================================
GWANGHWAMUN_LAT = 37.5759
GWANGHWAMUN_LNG = 126.9769
FOOD_FILE = os.path.join(os.path.dirname(__file__) or '.', 'food_db.json')

FOOD_CATEGORIES = ["한식", "일식", "중식", "양식", "카페", "분식", "해산물", "고기", "면류", "기타"]
FOOD_MENU_LIST = [
    "국밥", "김치찌개", "된장찌개", "순두부찌개", "부대찌개", "비빔밥", "불고기", "삼겹살",
    "갈비탕", "설렁탕", "해장국", "칼국수", "수제비", "냉면", "콩국수", "떡볶이",
    "돈까스", "초밥", "라멘", "우동", "덮밥",
    "짜장면", "짬뽕", "마라탕", "마라샹궈",
    "파스타", "피자", "스테이크", "햄버거", "샐러드", "브런치",
    "치킨", "족발", "보쌈", "한우", "오마카세", "한정식", "코스요리",
    "샤브샤브", "곰탕", "백반", "김밥", "전/파전", "해물탕",
]
MOOD_TAGS = {
    "피곤": ["해장국", "국밥", "순두부찌개", "칼국수", "설렁탕"],
    "기쁨": ["스테이크", "초밥", "파스타", "오마카세", "한우"],
    "스트레스": ["마라탕", "떡볶이", "삼겹살", "치킨", "마라샹궈"],
    "선택장애": [],  # 룰렛용
    "플렉스": ["한우", "오마카세", "코스요리", "스테이크", "한정식"],
}
WEATHER_TAGS = {
    "맑음": ["샐러드", "냉면", "브런치", "비빔밥"],
    "흐림": ["국밥", "김치찌개", "라멘", "칼국수"],
    "비/눈": ["칼국수", "수제비", "전/파전", "해물탕"],
    "폭염": ["냉면", "콩국수", "초밥", "샐러드"],
    "한파": ["설렁탕", "갈비탕", "부대찌개", "샤브샤브", "곰탕"],
}
COMPANION_TAGS = {
    "혼밥": ["덮밥", "국밥", "라멘", "김밥", "백반"],
    "동료": ["김치찌개", "된장찌개", "백반", "비빔밥"],
    "연인": ["파스타", "스테이크", "오마카세", "브런치", "코스요리"],
    "비즈니스": ["한정식", "코스요리", "한우", "갈비탕"],
}

def _load_food_db():
    if os.path.exists(FOOD_FILE):
        with open(FOOD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def _save_food_db(data):
    with open(FOOD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _haversine(lat1, lng1, lat2, lng2):
    R = 6371000
    p = math.pi / 180
    a = 0.5 - math.cos((lat2-lat1)*p)/2 + math.cos(lat1*p)*math.cos(lat2*p)*(1-math.cos((lng2-lng1)*p))/2
    return R * 2 * math.asin(math.sqrt(a))

def fetch_naver_restaurants(keyword="광화문 맛집", pages=5):
    """네이버 지역 검색 API로 맛집 수집 (2km 이내 필터)"""
    results = []
    seen = set()
    for start in range(1, pages * 5 + 1, 5):
        url = f"https://openapi.naver.com/v1/search/local.json?query={urllib.parse.quote(keyword)}&display=5&start={start}&sort=comment"
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", CLIENT_ID)
        req.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode('utf-8'))
                for item in data.get('items', []):
                    title = re.sub(r'<.*?>', '', item.get('title', ''))
                    if title in seen:
                        continue
                    # 좌표 변환 (카텍 → 없으면 스킵)
                    mapx = float(item.get('mapx', 0)) / 1e7 if len(str(item.get('mapx',''))) > 7 else float(item.get('mapx', 0))
                    mapy = float(item.get('mapy', 0)) / 1e7 if len(str(item.get('mapy',''))) > 7 else float(item.get('mapy', 0))

                    if mapx == 0 or mapy == 0:
                        dist = 0
                    else:
                        dist = _haversine(GWANGHWAMUN_LAT, GWANGHWAMUN_LNG, mapy, mapx)

                    if dist > 2000 and dist != 0:
                        continue

                    category = item.get('category', '기타')
                    seen.add(title)
                    results.append({
                        "name": title,
                        "category": category,
                        "address": item.get('roadAddress', '') or item.get('address', ''),
                        "link": item.get('link', ''),
                        "distance": round(dist),
                        "source": "naver",
                    })
        except Exception:
            break
    return results

def search_restaurants_by_menu(menu, pages=3):
    """메뉴명으로 광화문 근처 식당 검색 → 네이버지도 링크 포함"""
    keyword = f"광화문 {menu}"
    results = []
    seen = set()
    for start in range(1, pages * 5 + 1, 5):
        url = f"https://openapi.naver.com/v1/search/local.json?query={urllib.parse.quote(keyword)}&display=5&start={start}&sort=comment"
        req = urllib.request.Request(url)
        req.add_header("X-Naver-Client-Id", CLIENT_ID)
        req.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
        try:
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode('utf-8'))
                for item in data.get('items', []):
                    title = re.sub(r'<.*?>', '', item.get('title', ''))
                    if title in seen:
                        continue
                    mapx = float(item.get('mapx', 0)) / 1e7 if len(str(item.get('mapx', ''))) > 7 else float(item.get('mapx', 0))
                    mapy = float(item.get('mapy', 0)) / 1e7 if len(str(item.get('mapy', ''))) > 7 else float(item.get('mapy', 0))
                    if mapx == 0 or mapy == 0:
                        dist = 0
                    else:
                        dist = _haversine(GWANGHWAMUN_LAT, GWANGHWAMUN_LNG, mapy, mapx)
                    if dist > 2000 and dist != 0:
                        continue
                    seen.add(title)
                    naver_map_url = f"https://map.naver.com/v5/search/{urllib.parse.quote(title + ' 광화문')}"
                    results.append({
                        "name": title,
                        "category": item.get('category', ''),
                        "address": item.get('roadAddress', '') or item.get('address', ''),
                        "distance": round(dist),
                        "naver_map": naver_map_url,
                        "link": item.get('link', ''),
                    })
        except Exception:
            break
    results.sort(key=lambda x: x.get('distance', 9999))
    return results

def _match_score(rest, weather, mood, companion):
    """조건 매칭 점수 (0~10)"""
    score = 0
    name_cat = (rest.get('name','') + ' ' + rest.get('category','')).lower()

    if mood and mood in MOOD_TAGS:
        for tag in MOOD_TAGS[mood]:
            if tag in name_cat:
                score += 3
                break
    if weather and weather in WEATHER_TAGS:
        for tag in WEATHER_TAGS[weather]:
            if tag in name_cat:
                score += 3
                break
    if companion and companion in COMPANION_TAGS:
        for tag in COMPANION_TAGS[companion]:
            if tag in name_cat:
                score += 3
                break
    # 거리 보너스
    dist = rest.get('distance', 9999)
    if dist < 500:
        score += 1
    return score


# ==========================================
# 7. 메인 UI 및 컨트롤 패널
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ 수집 기준 설정")
    search_days = st.slider("조회 기간 (N일 전부터)", 1, 7, 1)
    search_hour = st.slider("조회 기준 시간 (시)", 0, 23, 0)

    now_kst = datetime.now(KST)
    target_date = (now_kst - timedelta(days=search_days-1)).replace(hour=search_hour, minute=0, second=0, microsecond=0)
    st.info(f"📍 갱신 기준:\n**{target_date.strftime('%Y-%m-%d %H:%M')}** 이후 기사")

    st.divider()

    st.markdown("### 📺 OTT 검색어")
    ott_keyword = st.text_input("OTT 검색어", value="티빙 웨이브")

    st.divider()

    st.caption(f"🏢 KT 그룹사: {len(KT_COMPANIES_MAP)}개 대상 일괄 수집")
    btn_all = st.button("🚀 통합 데이터 갱신", use_container_width=True)

# --- 첫 진입 시 1일 기준 자동 조회 ---
if 'auto_loaded' not in st.session_state:
    st.session_state['auto_loaded'] = True
    btn_all = True  # 자동 갱신 트리거

# --- 탭 구성 ---
tab_ott, tab_kt, tab_food = st.tabs(["📺 OTT 산업 기사검색", "🏢 KT 그룹사 기사검색", "🍽️ 광화문 맛집추천"])

# --- 통합 갱신 처리 ---
if btn_all:
    progress_bar = st.progress(0, text="🔍 검색 준비 중...")
    status_text = st.empty()

    status_text.markdown("**📺 OTT 산업 기사 검색 중...**")
    progress_bar.progress(10, text="📺 OTT 기사 수집 중...")
    df_v, df_f = fetch_ott_news(ott_keyword, target_date)
    st.session_state['ott_v'] = df_v
    st.session_state['ott_f'] = df_f
    progress_bar.progress(40, text=f"📺 OTT 완료 — 선별 {len(df_v)}건 / 차단 {len(df_f)}건")

    status_text.markdown(f"**🏢 KT 그룹사 {len(KT_COMPANIES_MAP)}개 병렬 검색 중...**")
    progress_bar.progress(50, text="🏢 KT 그룹사 기사 수집 중...")
    kt_df = fetch_all_kt_news(target_date)
    st.session_state['kt_df'] = kt_df
    progress_bar.progress(90, text=f"🏢 KT 완료 — {len(kt_df)}건 수집")

    progress_bar.progress(100, text="검색 완료")
    status_text.empty()
    progress_bar.empty()
    st.toast("통합 데이터 갱신 완료", icon="✅")

# --- [1] OTT 기사검색 탭 ---
with tab_ott:
    if 'ott_v' in st.session_state:
        df_v = st.session_state['ott_v']
        df_f = st.session_state['ott_f']

        # 미니 통계
        st.markdown(
            f'<div style="margin-bottom:20px;">'
            f'<span class="mini-stat">선별 <b>{len(df_v)}</b> 건</span>'
            f'<span class="mini-stat">차단 <b>{len(df_f)}</b> 건</span>'
            f'</div>',
            unsafe_allow_html=True
        )

        # 상위 4건 카드형 하이라이트
        if not df_v.empty:
            top4 = df_v.head(4).to_dict('records')
            # 이미지 병렬 수집
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
                imgs = list(ex.map(lambda r: fetch_article_image(r['기사링크']), top4))
            placeholder_img = "https://placehold.co/400x200/e2e8f0/94a3b8?text=No+Image"

            cols = st.columns(4)
            for i, (item, img_url) in enumerate(zip(top4, imgs)):
                tag_class = "tag-core"
                if "구출" in item.get('분류', ''):
                    tag_class = "tag-rescued"
                elif "일반" in item.get('분류', ''):
                    tag_class = "tag-normal"
                card_img = img_url if img_url else placeholder_img
                desc_text = item.get('요약', '')[:80]
                tag_label = item.get('분류', '').replace('✅ ', '').replace('⚡ ', '')
                with cols[i]:
                    st.markdown(
                        f'<a href="{item["기사링크"]}" target="_blank" style="text-decoration:none;">'
                        f'<div class="news-card">'
                        f'<img src="{card_img}" alt="thumbnail" onerror="this.src=\'{placeholder_img}\'">'
                        f'<div class="card-body">'
                        f'<div class="card-date">{item["발행일"]}</div>'
                        f'<div class="card-title">{item["제목"]}</div>'
                        f'<div class="card-desc">{desc_text}</div>'
                        f'<span class="card-tag {tag_class}">{tag_label}</span>'
                        f'</div></div></a>',
                        unsafe_allow_html=True
                    )

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        sub_tab1, sub_tab2 = st.tabs(["🎯 정제된 산업 뉴스", "🗑️ 차단된 홍보 기사"])
        with sub_tab1:
            st.dataframe(df_v, column_config={"기사링크": st.column_config.LinkColumn("Link", display_text="🔗 이동")}, hide_index=True, use_container_width=True, height=500)
        with sub_tab2:
            st.dataframe(df_f, column_config={"기사링크": st.column_config.LinkColumn("Link", display_text="🔗 이동")}, hide_index=True, use_container_width=True, height=500)
    else:
        st.info("왼쪽 패널에서 **[🚀 통합 데이터 갱신]** 버튼을 눌러주세요.")

    # --- 블랙리스트 / 화이트리스트 관리 ---
    with st.expander("⚙️ 필터 키워드 관리 (블랙리스트 / 화이트리스트)"):
        flt = st.session_state['ott_filters']

        ft1, ft2, ft3 = st.tabs(["🚫 블랙리스트", "⭐ 핵심 화이트", "📋 일반 화이트"])

        with ft1:
            st.caption(f"현재 {len(flt['black'])}개 — 이 단어가 포함되면 기사 차단")
            st.markdown(
                " ".join(f'`{w}`' for w in flt['black']),
                unsafe_allow_html=False
            )
            bc1, bc2 = st.columns([3, 1])
            with bc1:
                black_add = st.text_input("추가할 단어", key="black_add", placeholder="단어 입력 (쉼표로 여러개)")
            with bc2:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("➕ 추가", key="black_add_btn", use_container_width=True):
                    new_words = [w.strip() for w in black_add.split(",") if w.strip()]
                    added = [w for w in new_words if w not in flt['black']]
                    if added:
                        flt['black'].extend(added)
                        _save_filters(flt)
                        st.toast(f"블랙리스트 추가: {', '.join(added)}", icon="🚫")
                        st.rerun()
            black_del = st.multiselect("삭제할 단어 선택", flt['black'], key="black_del")
            if st.button("🗑️ 선택 삭제", key="black_del_btn"):
                if black_del:
                    flt['black'] = [w for w in flt['black'] if w not in black_del]
                    _save_filters(flt)
                    st.toast(f"블랙리스트에서 {len(black_del)}개 삭제", icon="✅")
                    st.rerun()

        with ft2:
            st.caption(f"현재 {len(flt['strong_white'])}개 — 이 단어가 있으면 핵심 산업 뉴스로 분류")
            st.markdown(
                " ".join(f'`{w}`' for w in flt['strong_white']),
                unsafe_allow_html=False
            )
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                strong_add = st.text_input("추가할 단어", key="strong_add", placeholder="단어 입력 (쉼표로 여러개)")
            with sc2:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("➕ 추가", key="strong_add_btn", use_container_width=True):
                    new_words = [w.strip() for w in strong_add.split(",") if w.strip()]
                    added = [w for w in new_words if w not in flt['strong_white']]
                    if added:
                        flt['strong_white'].extend(added)
                        _save_filters(flt)
                        st.toast(f"핵심 화이트 추가: {', '.join(added)}", icon="⭐")
                        st.rerun()
            strong_del = st.multiselect("삭제할 단어 선택", flt['strong_white'], key="strong_del")
            if st.button("🗑️ 선택 삭제", key="strong_del_btn"):
                if strong_del:
                    flt['strong_white'] = [w for w in flt['strong_white'] if w not in strong_del]
                    _save_filters(flt)
                    st.toast(f"핵심 화이트에서 {len(strong_del)}개 삭제", icon="✅")
                    st.rerun()

        with ft3:
            st.caption(f"현재 {len(flt['normal_white'])}개 — 이 단어가 있으면 일반 산업 뉴스로 분류")
            st.markdown(
                " ".join(f'`{w}`' for w in flt['normal_white']),
                unsafe_allow_html=False
            )
            nc1, nc2 = st.columns([3, 1])
            with nc1:
                normal_add = st.text_input("추가할 단어", key="normal_add", placeholder="단어 입력 (쉼표로 여러개)")
            with nc2:
                st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                if st.button("➕ 추가", key="normal_add_btn", use_container_width=True):
                    new_words = [w.strip() for w in normal_add.split(",") if w.strip()]
                    added = [w for w in new_words if w not in flt['normal_white']]
                    if added:
                        flt['normal_white'].extend(added)
                        _save_filters(flt)
                        st.toast(f"일반 화이트 추가: {', '.join(added)}", icon="📋")
                        st.rerun()
            normal_del = st.multiselect("삭제할 단어 선택", flt['normal_white'], key="normal_del")
            if st.button("🗑️ 선택 삭제", key="normal_del_btn"):
                if normal_del:
                    flt['normal_white'] = [w for w in flt['normal_white'] if w not in normal_del]
                    _save_filters(flt)
                    st.toast(f"일반 화이트에서 {len(normal_del)}개 삭제", icon="✅")
                    st.rerun()

        if st.button("🔄 기본값 복원", key="filter_reset"):
            st.session_state['ott_filters'] = {"black": list(_DEFAULT_BLACK), "strong_white": list(_DEFAULT_STRONG_WHITE), "normal_white": list(_DEFAULT_NORMAL_WHITE)}
            _save_filters(st.session_state['ott_filters'])
            st.toast("기본값으로 복원 완료", icon="🔄")
            st.rerun()

# --- [2] KT 그룹사 기사검색 탭 ---
with tab_kt:
    if 'kt_df' in st.session_state:
        kt_data_full = st.session_state['kt_df']
        if not kt_data_full.empty:
            st.markdown(
                f'<div style="margin-bottom:8px;">'
                f'<span class="mini-stat">총 <b>{len(kt_data_full)}</b> 건</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            # 멀티 선택 토글 칩
            st.markdown('<div class="kt-chips">', unsafe_allow_html=True)
            _short = {"KT/케이티": "KT", "스튜디오지니": "스지니", "KT ENA/ENA": "ENA",
                       "스카이라이프": "스카이", "밀리의서재": "밀리", "지니뮤직": "지니뮤직",
                       "나스미디어": "나스", "HCN": "HCN", "KT알파": "알파", "KT알티미디어": "알티"}
            short_names = {k: _short.get(k, k.split("/")[0]) for k in KT_COMPANIES_MAP}
            if 'kt_chips' not in st.session_state:
                st.session_state['kt_chips'] = set()  # 빈 셋 = 전체

            chip_cols = st.columns(len(KT_COMPANIES_MAP) + 1)
            # 전체 버튼
            with chip_cols[0]:
                all_active = len(st.session_state['kt_chips']) == 0
                lbl_all = ":: 전체" if all_active else "전체"
                if st.button(lbl_all, key="kt_chip_all", use_container_width=True,
                             type="primary" if all_active else "secondary"):
                    st.session_state['kt_chips'] = set()
                    st.rerun()
            # 개별 그룹사 버튼
            for i, comp in enumerate(KT_COMPANIES_MAP.keys()):
                with chip_cols[i + 1]:
                    is_on = comp in st.session_state['kt_chips']
                    lbl = f":: {short_names[comp]}" if is_on else short_names[comp]
                    if st.button(lbl, key=f"kt_chip_{i}", use_container_width=True,
                                 type="primary" if is_on else "secondary"):
                        if is_on:
                            st.session_state['kt_chips'].discard(comp)
                        else:
                            st.session_state['kt_chips'].add(comp)
                        st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)  # kt-chips 닫기

            # 필터 적용
            selected = st.session_state['kt_chips']
            kt_data = kt_data_full if not selected else kt_data_full[kt_data_full['그룹사명'].isin(selected)]

            st.dataframe(
                kt_data,
                column_config={
                    "그룹사명": st.column_config.TextColumn("그룹사", width="small"),
                    "발행일": st.column_config.TextColumn("발행일", width="small"),
                    "제목": st.column_config.TextColumn("기사 제목", width="large"),
                    "기사링크": st.column_config.LinkColumn("Link", display_text="🔗 원문이동")
                },
                hide_index=True,
                use_container_width=True,
                height=600
            )
        else:
            st.warning("해당 기간 내 수집된 그룹사 기사가 없습니다.")
    else:
        st.info("왼쪽 패널에서 **[🚀 통합 데이터 갱신]** 버튼을 눌러주세요.")

# --- [3] 광화문 맛집추천 탭 ---
_WEATHER_ICONS = {"맑음": "☀️", "흐림": "☁️", "비/눈": "🌧️", "폭염": "🌡️", "한파": "❄️"}
_MOOD_ICONS = {"피곤": "🔋", "기쁨": "✨", "스트레스": "⚡", "선택장애": "🎯", "플렉스": "💎"}
_COMP_ICONS = {"혼밥": "🧑", "동료": "👥", "연인": "❤️", "비즈니스": "💼"}

with tab_food:
    if 'sel_weather' not in st.session_state:
        st.session_state['sel_weather'] = None
    if 'sel_mood' not in st.session_state:
        st.session_state['sel_mood'] = None
    if 'sel_companion' not in st.session_state:
        st.session_state['sel_companion'] = None
    if 'roulette_menu' not in st.session_state:
        st.session_state['roulette_menu'] = None
    if 'roulette_restaurants' not in st.session_state:
        st.session_state['roulette_restaurants'] = []

    col_dial, col_result = st.columns([3, 4])

    # ========== 좌측: 다크 다이얼 패널 ==========
    with col_dial:
        st.markdown('<div class="dial-col">', unsafe_allow_html=True)
        st.markdown(
            '<div class="dark-dial">'
            '<div style="font-size:17px;font-weight:800;color:#fff;">⚡ 오늘의 매칭 다이얼 설정</div>'
            '<div style="font-size:12px;color:#a5b4fc;margin-bottom:18px;">오늘의 날씨, 내 마음의 상태, 함께 가는 사람을 골라보세요!</div>'
            '<div style="font-size:12px;font-weight:600;color:#94a3b8;margin-bottom:6px;">오늘의 날씨</div>'
            '</div>',
            unsafe_allow_html=True
        )
        _W_SHORT = {"비/눈": "비눈"}
        ww_cols = st.columns(len(WEATHER_TAGS))
        for i, w in enumerate(WEATHER_TAGS.keys()):
            with ww_cols[i]:
                is_on = st.session_state['sel_weather'] == w
                icon = _WEATHER_ICONS.get(w, "")
                lbl = _W_SHORT.get(w, w)
                if st.button(f"{icon}{lbl}", key=f"w_{w}", use_container_width=True,
                             type="primary" if is_on else "secondary"):
                    st.session_state['sel_weather'] = w if not is_on else None
                    st.rerun()

        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#94a3b8;margin:10px 0 6px;">내 마음의 기분</div>',
            unsafe_allow_html=True
        )
        _M_SHORT = {"스트레스": "스트레", "선택장애": "선택장애", "플렉스": "플렉스"}
        mm_cols = st.columns(len(MOOD_TAGS))
        for i, m in enumerate(MOOD_TAGS.keys()):
            with mm_cols[i]:
                is_on = st.session_state['sel_mood'] == m
                icon = _MOOD_ICONS.get(m, "")
                lbl = _M_SHORT.get(m, m)
                if st.button(f"{icon}{lbl}", key=f"m_{m}", use_container_width=True,
                             type="primary" if is_on else "secondary"):
                    st.session_state['sel_mood'] = m if not is_on else None
                    st.rerun()

        st.markdown(
            '<div style="font-size:12px;font-weight:600;color:#94a3b8;margin:10px 0 6px;">누구와 함께 가나요?</div>',
            unsafe_allow_html=True
        )
        _C_SHORT = {"비즈니스": "비즈"}
        cc_cols = st.columns(len(COMPANION_TAGS))
        for i, c in enumerate(COMPANION_TAGS.keys()):
            with cc_cols[i]:
                is_on = st.session_state['sel_companion'] == c
                icon = _COMP_ICONS.get(c, "")
                lbl = _C_SHORT.get(c, c)
                if st.button(f"{icon}{lbl}", key=f"c_{c}", use_container_width=True,
                             type="primary" if is_on else "secondary"):
                    st.session_state['sel_companion'] = c if not is_on else None
                    st.rerun()

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        btn_spin = st.button("🎯  이 조건에 딱 맞는 인생식사 추천받기  ›", use_container_width=True,
                             type="primary", key="spin_roulette")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        btn_random = st.button("🌀  아무거나 맛집 고속 룰렛 타임  🎲", use_container_width=True, key="random_roulette")
        st.markdown('</div>', unsafe_allow_html=True)  # dial-col 닫기

    # ========== 메뉴 풀 계산 ==========
    weather = st.session_state.get('sel_weather')
    mood = st.session_state.get('sel_mood')
    companion = st.session_state.get('sel_companion')
    recommended_menus = []
    if weather and weather in WEATHER_TAGS:
        recommended_menus.extend(WEATHER_TAGS[weather])
    if mood and mood in MOOD_TAGS:
        recommended_menus.extend(MOOD_TAGS[mood])
    if companion and companion in COMPANION_TAGS:
        recommended_menus.extend(COMPANION_TAGS[companion])
    menu_pool = list(FOOD_MENU_LIST)
    if recommended_menus:
        display_pool = list(dict.fromkeys(m for m in recommended_menus if m in menu_pool))
        if not display_pool:
            display_pool = menu_pool
    else:
        display_pool = menu_pool

    # ========== 룰렛 실행 ==========
    if btn_spin or btn_random:
        pool = display_pool if btn_spin else menu_pool
        with col_result:
            spin_placeholder = st.empty()
            # 스피닝 애니메이션
            random.shuffle(pool)
            spin_items = (pool * 6)[:30]
            slot_html = "".join(f'<div class="slot-item">{m}</div>' for m in spin_items)
            spin_placeholder.markdown(
                f'<div class="roulette-window">'
                f'<div style="font-size:14px;color:#a5b4fc;margin-bottom:8px;font-weight:600;">🎰 돌리는 중...</div>'
                f'<div style="height:80px;overflow:hidden;position:relative;">'
                f'<div class="slot-track">{slot_html}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
        time.sleep(1.8)
        pick_menu = random.choice(pool)
        st.session_state['roulette_menu'] = pick_menu
        with col_result:
            spin_placeholder.markdown(
                f'<div class="roulette-window">'
                f'<div style="font-size:14px;color:#a5b4fc;font-weight:600;">🔍 광화문 근처 "{pick_menu}" 식당 검색 중...</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        restaurants = search_restaurants_by_menu(pick_menu)
        st.session_state['roulette_restaurants'] = restaurants
        st.balloons()
        st.rerun()

    # ========== 우측: 결과 패널 ==========
    with col_result:
        if st.session_state['roulette_menu']:
            pick_menu = st.session_state['roulette_menu']
            restaurants = st.session_state['roulette_restaurants']
            naver_search_url = f"https://map.naver.com/v5/search/{urllib.parse.quote('광화문 ' + pick_menu)}"

            # 결과 패널 시작
            top_rest = restaurants[0] if restaurants else None
            rest_count = len(restaurants)

            # 헤더
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-header">'
                f'<div class="result-header-title">🍽️ 오늘의 식탁 선택</div>'
                f'<span class="result-badge">총 {rest_count}개 후보점</span>'
                f'</div>',
                unsafe_allow_html=True
            )

            if top_rest:
                cat_label = top_rest.get('category', '').split('>')[0].strip() if top_rest.get('category') else pick_menu
                dist_text = f"{top_rest['distance']}m" if top_rest.get('distance') else ""

                st.markdown(
                    f'<span class="result-cat-tag">{cat_label} 🍳</span>'
                    f'<a href="{naver_search_url}" target="_blank" '
                    f'style="float:right;background:#6366f1;color:#fff;font-size:11px;font-weight:700;'
                    f'padding:6px 14px;border-radius:10px;text-decoration:none;">✨ 네이버지도 검색</a>'
                    f'<div style="clear:both;"></div>'
                    f'<div class="rest-top-name">{top_rest["name"]} '
                    f'<span class="rest-top-rating">⭐</span></div>'
                    f'<div class="rest-top-desc">'
                    f'광화문역 인근에서 "{pick_menu}"으로 유명한 맛집입니다. '
                    f'네이버 리뷰 기준 인기 상위 식당으로, 점심시간에는 대기가 있을 수 있습니다.</div>',
                    unsafe_allow_html=True
                )

                # 추천 코멘트 (다크 카드)
                condition_parts = []
                if weather:
                    condition_parts.append(f"{_WEATHER_ICONS.get(weather,'')} {weather}")
                if mood:
                    condition_parts.append(f"{_MOOD_ICONS.get(mood,'')} {mood}")
                if companion:
                    condition_parts.append(f"{_COMP_ICONS.get(companion,'')} {companion}")
                condition_text = " + ".join(condition_parts) if condition_parts else "랜덤"

                st.markdown(
                    f'<div class="rest-quote">'
                    f'<div class="rest-quote-badge">🟢 광화문 선배 보스의 특급 평결</div>'
                    f'<div class="rest-quote-text">'
                    f'"오늘 같은 [{condition_text}] 날에는 {pick_menu}이 딱이지! '
                    f'광화문 피맛골을 지켜온 \'{top_rest["name"]}\'이 정답이야! '
                    f'결정 장애 제대로 온 부서 사람들 다 같이 이끌고 갈 때는 고민할 필요 없어. '
                    f'일단 가면 반은 해결이야."</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # 식당 정보
                st.markdown(
                    f'<div class="rest-info-row">'
                    f'<div class="rest-info-icon">📍</div>'
                    f'<div class="rest-info-label">위치 알림</div>'
                    f'<div class="rest-info-value">{top_rest.get("address", "광화문 인근")} ({dist_text})</div>'
                    f'</div>'
                    f'<div class="rest-info-row">'
                    f'<div class="rest-info-icon">🍴</div>'
                    f'<div class="rest-info-label">추천 메뉴</div>'
                    f'<div class="rest-info-value price">{pick_menu}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # 오피스 꿀팁
                st.markdown(
                    f'<div class="rest-tip-box">'
                    f'<div class="rest-tip-title">🍽️ 오늘의 추천 메뉴 조합</div>'
                    f'<div class="rest-tip-text">💡 {top_rest["name"]}에서 {pick_menu}을(를) 기본으로 깔고, '
                    f'사이드 메뉴 하나 시켜서 나눠 먹는 조합 추천!</div>'
                    f'<div class="rest-tip-title" style="margin-top:10px;">오피스 꿀팁</div>'
                    f'<div class="rest-tip-text">날씨가 좋은 날엔 웨이팅 줄이 빌딩 밖까지 늘어서지만, '
                    f'회전율이 광속 수준이라 10~15분이면 금방 빠지니 걱정 마! '
                    f'다 먹고 나와서 바로 옆 청계천 산책로 한 바퀴 돌며 테이크아웃 커피 한 잔 때리는 게 '
                    f'광화문 고인물의 정석 코스란다.</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div style="text-align:center;padding:40px;color:#94a3b8;">'
                    f'<div style="font-size:36px;margin-bottom:8px;">🍳</div>'
                    f'<div>검색 결과가 없습니다.</div>'
                    f'<a href="{naver_search_url}" target="_blank" style="color:#6366f1;">네이버지도에서 직접 검색 →</a>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)  # result-panel 닫기

            # 나머지 식당 리스트
            if len(restaurants) > 1:
                st.markdown(
                    f'<div style="margin:20px 0 10px;font-size:14px;font-weight:700;color:#1e293b;">'
                    f'📍 "{pick_menu}" 주변 식당 {rest_count}곳</div>',
                    unsafe_allow_html=True
                )
                for idx, r in enumerate(restaurants[:10]):
                    dist_text = f"{r['distance']}m" if r.get('distance') else ""
                    map_url = r.get('naver_map', '')
                    links_html = f'<a href="{map_url}" target="_blank">🗺️ 네이버지도</a>'
                    if r.get('link'):
                        links_html += f' <a href="{r["link"]}" target="_blank">ℹ️ 상세</a>'
                    st.markdown(
                        f'<div class="rest-list-card">'
                        f'<div class="rest-rank">{idx+1}</div>'
                        f'<div class="rest-info">'
                        f'<div class="rest-name">{r["name"]}</div>'
                        f'<div class="rest-meta">{r.get("category","")} · {r.get("address","")} · {dist_text}</div>'
                        f'</div>'
                        f'<div class="rest-links">{links_html}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # 하단 버튼
            if st.button("🔄 다시 돌리기", key="respin", use_container_width=True):
                st.session_state['roulette_menu'] = None
                st.session_state['roulette_restaurants'] = []
                st.rerun()

        else:
            # 초기 상태 — 안내 메시지
            st.markdown(
                '<div class="result-panel" style="display:flex;align-items:center;justify-content:center;'
                'flex-direction:column;min-height:500px;">'
                '<div style="font-size:52px;margin-bottom:16px;">🍽️</div>'
                '<div style="font-size:18px;font-weight:700;color:#1e293b;margin-bottom:8px;">오늘의 식탁 선택</div>'
                '<div style="font-size:13px;color:#94a3b8;text-align:center;line-height:1.6;">'
                '왼쪽에서 날씨, 기분, 동행을 선택하고<br>'
                '<b>인생식사 추천받기</b> 버튼을 누르세요!<br>'
                '또는 <b>고속 룰렛</b>으로 바로 결정!</div>'
                '</div>',
                unsafe_allow_html=True
            )