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
        padding: 28px 32px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 24px rgba(99,102,241,0.08), 0 1px 3px rgba(0,0,0,0.06);
    }
    .header-title {
        color: #0f172a;
        font-size: 26px;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.5px;
    }
    .header-subtitle { color: #64748b; font-size: 14px; margin-top: 6px; letter-spacing: 0.3px; }
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
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <div>
        <h1 class="header-title">📡 Strategic Intelligence Dashboard <span style="font-size:11px; background: linear-gradient(135deg, #6366f1, #8b5cf6); padding:3px 10px; border-radius:12px; font-weight:600;">V3.1</span></h1>
        <div class="header-subtitle">OTT 산업 동향 및 KT 그룹사 통합 뉴스 기사검색 시스템</div>
    </div>
    <div style="background: #f0fdf4; padding:6px 14px; border-radius:20px; border:1px solid #bbf7d0; font-size:12px; color:#16a34a;">
        ● System Online
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
OTT_BLACK_LIST = ["출연", "캐스팅", "첫방", "시청률", "아이돌", "배우", "드라마", "예능", "화제", "포토", "종영", "비하인드", "팬미팅", "제작발표회", "라인업", "시즌2", "결말", "티저", "감독", "예고편", "포스터", "신작", "몇부작", "연기", "정체", "시청자", "관전포인트", "스포일러", "안방극장", "스크린", "줄거리", "회차", "번개맨", "애니메이션", "공개", "스트리밍", "시청 가능", "시청하기", "볼 수 있", "감상", "독점 공개", "론칭", "오리지널 시리즈", "오리지널 콘텐츠", "편성", "방영", "개봉"]
OTT_STRONG_WHITE = ["인수", "지분", "실적", "공정위", "구조조정", "적자", "흑자", "매출", "투자", "MAU", "점유율", "가입자", "기업결합", "시너지", "주주", "재무", "매각", "영업이익"]
OTT_NORMAL_WHITE = ["전략", "대표", "규제", "토종", "연합", "광고", "요금제", "영입", "플랫폼", "동향", "경쟁", "무료", "생존", "이용률", "출시", "생태계"]

# --- [KT 관련 검색 및 필터링 사전] ---
KT_COMPANIES_MAP = {
    "KT/케이티": '"KT" | "케이티" | "Korea Telecom"',
    "스튜디오지니": '"KT스튜디오지니" | "스튜디오지니"',
    "KT ENA/ENA": '"KT ENA" | "ENA 채널" | "채널 ENA"',
    "스카이라이프": '"KT스카이라이프" | "케이티스카이라이프" | "스카이라이프"',
    "밀리의서재": '"밀리의서재" | "밀리의 서재"',
    "지니뮤직": '"지니뮤직" | "KT지니뮤직"',
    "나스미디어": '"나스미디어" | "KT나스미디어"',
    "스토리위즈": '"스토리위즈" | "KT스토리위즈"',
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
    "스토리위즈": [r"스토리위즈", r"KT\s*스토리위즈"],
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
            if any(w in body_text for w in OTT_STRONG_WHITE):
                return True, "✅ 핵심 산업 (본문 감지)"
            if any(w in body_text for w in OTT_NORMAL_WHITE):
                return True, "✅ 일반 산업 (본문 감지)"
    
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
                    
                    news_data = {"발행일": dt.strftime("%m-%d %H:%M"), "제목": title, "기사링크": link, "분류": reason}
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
# 6. 메인 UI 및 컨트롤 패널
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ 수집 기준 설정")
    search_days = st.slider("조회 기간 (N일 전부터)", 1, 7, 3)
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

# --- 탭 구성 ---
tab_ott, tab_kt = st.tabs(["📺 OTT 산업 기사검색", "🏢 KT 그룹사 기사검색"])

# --- 통합 갱신 처리 ---
if btn_all:
    with st.spinner('OTT 산업 및 KT 그룹사 기사를 통합 수집 중입니다...'):
        df_v, df_f = fetch_ott_news(ott_keyword, target_date)
        st.session_state['ott_v'] = df_v
        st.session_state['ott_f'] = df_f

        kt_df = fetch_all_kt_news(target_date)
        st.session_state['kt_df'] = kt_df

# --- [1] OTT 기사검색 탭 ---
with tab_ott:
    if 'ott_v' in st.session_state:
        m1, m2 = st.columns(2)
        m1.metric("선별된 타겟 기사", f"{len(st.session_state['ott_v'])} 건")
        m2.metric("필터링된 노이즈", f"{len(st.session_state['ott_f'])} 건")
        
        sub_tab1, sub_tab2 = st.tabs(["🎯 정제된 산업 뉴스", "🗑️ 차단된 홍보 기사"])
        with sub_tab1:
            st.dataframe(st.session_state['ott_v'], column_config={"기사링크": st.column_config.LinkColumn("Link", display_text="🔗 이동")}, hide_index=True, use_container_width=True, height=500)
        with sub_tab2:
            st.dataframe(st.session_state['ott_f'], column_config={"기사링크": st.column_config.LinkColumn("Link", display_text="🔗 이동")}, hide_index=True, use_container_width=True, height=500)
    else:
        st.info("왼쪽 패널에서 **[🚀 통합 데이터 갱신]** 버튼을 눌러주세요.")

# --- [2] KT 그룹사 기사검색 탭 ---
with tab_kt:
    if 'kt_df' in st.session_state:
        kt_data = st.session_state['kt_df']
        if not kt_data.empty:
            st.metric("총 수집된 그룹사 기사", f"{len(kt_data)} 건")
            
            # 그룹사 필터 기능
            selected_comp = st.selectbox("📂 특정 그룹사만 보기", ["전체 보기"] + list(KT_COMPANIES_MAP.keys()))
            if selected_comp != "전체 보기":
                kt_data = kt_data[kt_data['그룹사명'] == selected_comp]
                
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