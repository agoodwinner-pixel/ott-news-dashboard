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
    /* KT 그룹사 토글 칩 — 한 줄 고정 */
    [data-testid="stHorizontalBlock"] .stButton>button {
        font-size: 10px !important;
        padding: 2px 4px !important;
        height: 28px !important;
        min-height: 28px !important;
        border-radius: 6px !important;
        white-space: nowrap !important;
    }
    [data-testid="stHorizontalBlock"] .stButton>button[kind="primary"],
    [data-testid="stHorizontalBlock"] .stButton>button[data-testid="stBaseButton-primary"] {
        background: #4f46e5 !important;
        color: #ffffff !important;
        border: 2px solid #4f46e5 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(79,70,229,0.3) !important;
    }
    [data-testid="stHorizontalBlock"] .stButton>button[kind="secondary"],
    [data-testid="stHorizontalBlock"] .stButton>button[data-testid="stBaseButton-secondary"] {
        background: #f1f5f9 !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
    }
    [data-testid="stBaseButton-primary"]>button {
        background: #4f46e5 !important;
        color: #ffffff !important;
        border: 2px solid #4f46e5 !important;
        box-shadow: 0 2px 8px rgba(79,70,229,0.3) !important;
    }
    [data-testid="stBaseButton-secondary"]>button {
        background: #f1f5f9 !important;
        color: #64748b !important;
        border: 1px solid #e2e8f0 !important;
    }
    /* 맛집 탭 스타일 */
    .food-section-label {
        font-size: 12px;
        font-weight: 700;
        color: #475569;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .food-card {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
        padding: 18px 20px;
        margin-bottom: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }
    .food-card:hover {
        box-shadow: 0 6px 20px rgba(99,102,241,0.10);
        transform: translateY(-1px);
    }
    .food-card .food-name {
        font-size: 15px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 4px;
    }
    .food-card .food-cat {
        display: inline-block;
        font-size: 10px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 10px;
        background: #ede9fe;
        color: #7c3aed;
        margin-bottom: 6px;
    }
    .food-card .food-addr {
        font-size: 11px;
        color: #94a3b8;
    }
    .food-roulette {
        text-align: center;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        border-radius: 16px;
        padding: 36px 24px;
        margin: 16px 0;
        box-shadow: 0 8px 24px rgba(99,102,241,0.25);
    }
    .food-roulette .pick-name {
        font-size: 26px;
        font-weight: 800;
        color: #fff;
        margin: 10px 0 4px;
    }
    .food-roulette .pick-info {
        font-size: 13px;
        color: #e2e8f0;
    }
    .food-roulette .pick-addr {
        font-size: 11px;
        color: #cbd5e1;
        margin-top: 4px;
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
MOOD_TAGS = {
    "피곤": ["해장국", "국밥", "순두부", "칼국수", "죽"],
    "기쁨": ["스테이크", "초밥", "파스타", "오마카세", "뷔페"],
    "스트레스": ["매운탕", "떡볶이", "닭볶음탕", "불닭", "마라탕"],
    "선택장애": [],  # 룰렛용
    "플렉스": ["한우", "오마카세", "코스요리", "스테이크", "와인바"],
}
WEATHER_TAGS = {
    "맑음": ["테라스", "야외", "샐러드", "냉면"],
    "흐림": ["국밥", "찌개", "라멘"],
    "비/눈": ["칼국수", "수제비", "전", "파전", "해물탕"],
    "폭염": ["냉면", "콩국수", "빙수", "아이스", "냉모밀"],
    "한파": ["설렁탕", "갈비탕", "부대찌개", "샤브샤브", "곰탕"],
}
COMPANION_TAGS = {
    "혼밥": ["덮밥", "국밥", "라멘", "김밥", "백반"],
    "동료": ["한식", "중식", "백반", "찌개"],
    "연인": ["파스타", "스테이크", "오마카세", "와인바", "브런치"],
    "비즈니스": ["한정식", "코스요리", "한우", "룸"],
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
with tab_food:
    # DB 로드
    if 'food_db' not in st.session_state:
        st.session_state['food_db'] = _load_food_db()
    food_db = st.session_state['food_db']

    # 헤더
    fh1, fh2 = st.columns([4, 1])
    with fh1:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;margin-bottom:2px;">'
            '<span style="font-size:15px;font-weight:700;color:#1e293b;">광화문 맛집 추천</span>'
            f'<span class="mini-stat" style="margin:0;">등록 <b>{len(food_db)}</b> 곳</span>'
            '</div>'
            '<div style="font-size:11px;color:#94a3b8;">광화문 중심 2km 이내 · 날씨/기분/동행 기반 추천</div>',
            unsafe_allow_html=True
        )
    with fh2:
        if st.button("🔄 맛집 DB 갱신", key="food_refresh", use_container_width=True):
            with st.spinner("네이버 맛집 검색 중..."):
                new_list = fetch_naver_restaurants("광화문 맛집", pages=5)
                new_list += fetch_naver_restaurants("종로 맛집", pages=3)
                new_list += fetch_naver_restaurants("세종로 맛집", pages=3)
                seen_names = set()
                deduped = []
                for r in new_list:
                    if r['name'] not in seen_names:
                        seen_names.add(r['name'])
                        deduped.append(r)
                _save_food_db(deduped)
                st.session_state['food_db'] = deduped
            st.toast(f"맛집 {len(deduped)}곳 수집 완료!", icon="✅")
            st.rerun()

    if not food_db:
        st.info("맛집 데이터가 없습니다. **[🔄 맛집 DB 갱신]** 버튼을 눌러 네이버에서 맛집을 수집해주세요.")
    else:
        # --- 조건 선택 ---
        if 'sel_weather' not in st.session_state:
            st.session_state['sel_weather'] = None
        if 'sel_mood' not in st.session_state:
            st.session_state['sel_mood'] = None
        if 'sel_companion' not in st.session_state:
            st.session_state['sel_companion'] = None

        st.markdown('<div class="food-section-label">🌤️ 날씨</div>', unsafe_allow_html=True)
        w_cols = st.columns(len(WEATHER_TAGS))
        for i, w in enumerate(WEATHER_TAGS.keys()):
            with w_cols[i]:
                is_on = st.session_state['sel_weather'] == w
                lbl = f":: {w}" if is_on else w
                if st.button(lbl, key=f"w_{w}", use_container_width=True,
                             type="primary" if is_on else "secondary"):
                    st.session_state['sel_weather'] = w if not is_on else None
                    st.rerun()

        st.markdown('<div class="food-section-label">😊 기분</div>', unsafe_allow_html=True)
        m_cols = st.columns(len(MOOD_TAGS))
        for i, m in enumerate(MOOD_TAGS.keys()):
            with m_cols[i]:
                is_on = st.session_state['sel_mood'] == m
                lbl = f":: {m}" if is_on else m
                if st.button(lbl, key=f"m_{m}", use_container_width=True,
                             type="primary" if is_on else "secondary"):
                    st.session_state['sel_mood'] = m if not is_on else None
                    st.rerun()

        st.markdown('<div class="food-section-label">👥 동행</div>', unsafe_allow_html=True)
        c_cols = st.columns(len(COMPANION_TAGS))
        for i, c in enumerate(COMPANION_TAGS.keys()):
            with c_cols[i]:
                is_on = st.session_state['sel_companion'] == c
                lbl = f":: {c}" if is_on else c
                if st.button(lbl, key=f"c_{c}", use_container_width=True,
                             type="primary" if is_on else "secondary"):
                    st.session_state['sel_companion'] = c if not is_on else None
                    st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # --- 추천 버튼 ---
        rec_col1, rec_col2 = st.columns(2)
        with rec_col1:
            btn_recommend = st.button("🎯 조건 맞춤 추천", use_container_width=True, type="primary")
        with rec_col2:
            btn_roulette = st.button("🎰 랜덤 룰렛", use_container_width=True)

        # --- 추천 결과 ---
        if btn_recommend:
            weather = st.session_state.get('sel_weather')
            mood = st.session_state.get('sel_mood')
            companion = st.session_state.get('sel_companion')

            scored = []
            for r in food_db:
                s = _match_score(r, weather, mood, companion)
                scored.append((s, r))
            scored.sort(key=lambda x: (-x[0], x[1].get('distance', 9999)))
            top = scored[:6]

            if top[0][0] == 0 and not weather and not mood and not companion:
                st.warning("조건을 하나 이상 선택해주세요!")
            else:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                r_cols = st.columns(3)
                for i, (score, rest) in enumerate(top):
                    with r_cols[i % 3]:
                        dist_text = f"{rest['distance']}m" if rest.get('distance') else "거리 미상"
                        link_btn = f'<a href="{rest["link"]}" target="_blank" style="font-size:11px;color:#6366f1;text-decoration:none;font-weight:600;">상세보기 →</a>' if rest.get('link') else ''
                        stars = "⭐" * min(score, 5) if score > 0 else ""
                        st.markdown(
                            f'<div class="food-card">'
                            f'<div class="food-name">{rest["name"]} {stars}</div>'
                            f'<span class="food-cat">{rest.get("category","")}</span>'
                            f'<div class="food-addr">📍 {rest.get("address","")} · {dist_text}</div>'
                            f'<div style="margin-top:6px;">{link_btn}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

        if btn_roulette:
            if food_db:
                pick = random.choice(food_db)
                st.balloons()
                dist_text = f"{pick['distance']}m" if pick.get('distance') else ""
                link_html = f'<a href="{pick["link"]}" target="_blank" style="color:#e2e8f0;font-size:12px;">상세보기 →</a>' if pick.get('link') else ''
                st.markdown(
                    f'<div class="food-roulette">'
                    f'<div style="font-size:44px;">🎉</div>'
                    f'<div class="pick-name">{pick["name"]}</div>'
                    f'<div class="pick-info">{pick.get("category","")} · {dist_text}</div>'
                    f'<div class="pick-addr">📍 {pick.get("address","")}</div>'
                    f'<div style="margin-top:10px;">{link_html}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        # --- 맛집 관리 (추가/삭제) ---
        with st.expander("📝 맛집 직접 관리 (추가/삭제)", expanded=False):
            st.markdown('<div class="food-section-label">맛집 추가</div>', unsafe_allow_html=True)
            add_c1, add_c2, add_c3 = st.columns([2, 1, 2])
            with add_c1:
                new_name = st.text_input("가게명", key="food_new_name", label_visibility="collapsed", placeholder="가게명")
            with add_c2:
                new_cat = st.selectbox("카테고리", FOOD_CATEGORIES, key="food_new_cat", label_visibility="collapsed")
            with add_c3:
                new_addr = st.text_input("주소", key="food_new_addr", label_visibility="collapsed", placeholder="주소 (선택)")
            if st.button("➕ 추가", key="food_add"):
                if new_name.strip():
                    food_db.append({
                        "name": new_name.strip(),
                        "category": new_cat,
                        "address": new_addr.strip(),
                        "link": "",
                        "distance": 0,
                        "source": "manual",
                    })
                    _save_food_db(food_db)
                    st.session_state['food_db'] = food_db
                    st.toast(f"'{new_name}' 추가 완료!", icon="✅")
                    st.rerun()
                else:
                    st.warning("가게명을 입력해주세요.")

            st.markdown('<div class="food-section-label" style="margin-top:12px;">맛집 삭제</div>', unsafe_allow_html=True)
            del_names = [r['name'] for r in food_db]
            del_sel = st.multiselect("삭제할 맛집 선택", del_names, key="food_del_sel", label_visibility="collapsed")
            if st.button("🗑️ 선택 삭제", key="food_del"):
                if del_sel:
                    food_db = [r for r in food_db if r['name'] not in del_sel]
                    _save_food_db(food_db)
                    st.session_state['food_db'] = food_db
                    st.toast(f"{len(del_sel)}곳 삭제 완료!", icon="🗑️")
                    st.rerun()