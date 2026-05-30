import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import email.utils

# ==========================================
# 1. 디자인 및 페이지 설정 (다크 테마 적용)
# ==========================================
st.set_page_config(page_title="OTT Intelligence Dashboard", page_icon="📡", layout="wide")

# 이미지의 '광화문 식보스' 느낌을 차용한 고급스러운 다크/네이비 커스텀 CSS
st.markdown("""
    <style>
    /* 전체 배경색 다크 네이비로 변경 */
    .stApp {
        background-color: #121826;
        color: #e2e8f0;
    }
    
    /* 상단 헤더 컨테이너 스타일링 */
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title {
        color: #f8fafc;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 5px;
    }
    
    /* 지표(Metric) 카드 스타일 */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    /* 탭 메뉴 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: 1px solid #334155;
        border-bottom: none;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }

    /* 데이터프레임 배경 투명하게 */
    .stDataFrame {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #334155;
    }
    
    /* 버튼 스타일 (이미지 하단 버튼 참고) */
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border: none;
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #4338ca;
        border: none;
    }
    
    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 헤더 UI 렌더링
# ==========================================
# 이미지의 상단 배너 느낌을 살린 헤더 구성
st.markdown("""
<div class="header-box">
    <div>
        <h1 class="header-title">💼 OTT 전략·기획 관제소 <span style="font-size:12px; background-color:#4f46e5; padding:2px 8px; border-radius:12px;">V2.0 PRO</span></h1>
        <div class="header-subtitle">콘트롤 타워 전략 담당자를 위한 실시간 산업 동향 정제 시스템</div>
    </div>
    <div style="background-color:#1e293b; padding:5px 12px; border-radius:20px; border:1px solid #334155; font-size:12px; color:#94a3b8;">
        🟢 Live Monitoring Active
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 3. API 키 및 정밀 필터링 설정
# ==========================================
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception as e:
    st.error("🚨 API 키를 Streamlit Cloud Secrets에 설정해주세요.")
    st.stop()

# 🔴 1. 블랙리스트 (연예/홍보)
BLACK_LIST = ["출연", "캐스팅", "첫방", "시청률", "아이돌", "배우", "드라마", "예능", "화제", "포토", "종영", "비하인드", "팬미팅", "제작발표회", "라인업", "시즌2", "결말", "티저", "감독", "예고편", "포스터", "신작", "몇부작", "연기", "정체", "시청자", "관전포인트", "스포일러", "안방극장", "스크린", "줄거리", "회차", "번개맨", "애니메이션", "공개", "스트리밍"]

# 🔵 2. 강력 화이트리스트 (무조건 구출)
STRONG_WHITE_LIST = ["인수", "지분", "실적", "공정위", "구조조정", "적자", "흑자", "매출", "투자", "MAU", "점유율", "가입자", "기업결합", "시너지", "주주", "재무", "매각", "영업이익"]

# 🟡 3. 일반 화이트리스트 (블랙 없을때만)
NORMAL_WHITE_LIST = ["전략", "대표", "규제", "토종", "연합", "광고", "요금제", "영입", "플랫폼", "동향", "경쟁", "무료", "생존", "이용률", "출시", "생태계"]

def clean_html(text):
    text = re.sub(r'<.*?>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

def is_industry_news(title, description):
    full_text = title + " " + description
    has_black = any(word in full_text for word in BLACK_LIST)
    has_strong_white = any(word in full_text for word in STRONG_WHITE_LIST)
    has_normal_white = any(word in full_text for word in NORMAL_WHITE_LIST)
    
    if has_strong_white:
        if has_black: return True, "⚡ 강력 단어 구출"
        return True, "✅ 핵심 산업"
    if has_normal_white:
        if has_black: return False, "🚫 혼합(연예단어 포함)"
        return True, "✅ 일반 산업"
    if has_black: return False, "🚫 연예/홍보성"
    return False, "🚫 산업 단어 없음"

# ==========================================
# 4. 수집 엔진
# ==========================================
def fetch_all_news(query, days):
    target_date = (datetime.now() - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    
    valid_list, filtered_list = [], []
    
    for start_index in range(1, 1001, 100):
        params = {"query": query, "display": 100, "start": start_index, "sort": "date"}
        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code != 200:
                st.error(f"🚨 API 에러 (코드: {res.status_code})")
                break
                
            data = res.json()
            items = data.get('items', [])
            if not items: break
            
            for item in items:
                pub_date = email.utils.parsedate_to_datetime(item['pubDate']).replace(tzinfo=None)
                if pub_date < target_date:
                    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)
                
                title, desc = clean_html(item['title']), clean_html(item['description'])
                is_valid, reason = is_industry_news(title, desc)
                
                news_data = {
                    "발행일": pub_date.strftime("%m-%d %H:%M"),
                    "제목": title,
                    "기사링크": item['link'],
                    "분류": reason
                }
                if is_valid: valid_list.append(news_data)
                else: filtered_list.append(news_data)
                
        except Exception as e:
            st.error(f"🚨 에러: {e}")
            break
    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)

# ==========================================
# 5. 사이드바 및 메인 화면 제어
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ 제어 패널")
    search_keyword = st.text_input("검색어 설정", value="티빙 웨이브")
    search_days = st.slider("조회 기간 (일)", 1, 7, 3)
    update_btn = st.button("🚀 이 조건으로 데이터 갱신")
    
    st.divider()
    
    with st.expander("📚 필터링 단어 딕셔너리"):
        st.markdown("**🔵 무조건 구출 (Strong White)**")
        st.caption(", ".join(STRONG_WHITE_LIST))
        st.markdown("**🟡 일반 허용 (Normal White)**")
        st.caption(", ".join(NORMAL_WHITE_LIST))
        st.markdown("**🔴 절대 차단 (Black List)**")
        st.caption(", ".join(BLACK_LIST))

if update_btn:
    with st.spinner('실시간 분석 알고리즘 가동 중...'):
        df_v, df_f = fetch_all_news(search_keyword, search_days)
        st.session_state['df_v'] = df_v
        st.session_state['df_f'] = df_f

if 'df_v' in st.session_state:
    m1, m2, m3 = st.columns(3)
    m1.metric("선별된 타겟 기사", f"{len(st.session_state['df_v'])} 건")
    m2.metric("필터링된 노이즈", f"{len(st.session_state['df_f'])} 건")
    m3.metric("스캔 완료 기간", f"최근 {search_days}일")

    st.write("") # 간격

    # 이미지 스타일을 반영한 탭
    tab1, tab2 = st.tabs(["🎯 정제된 식탁 (유효 기사)", "🗑️ 버려진 메뉴 (차단 기사)"])
    
    with tab1:
        if not st.session_state['df_v'].empty:
            st.dataframe(
                st.session_state['df_v'],
                column_config={
                    "발행일": st.column_config.TextColumn("Time", width="small"),
                    "제목": st.column_config.TextColumn("Headline", width="large"),
                    "기사링크": st.column_config.LinkColumn("Link", display_text="🔗 이동"),
                    "분류": st.column_config.TextColumn("Status", width="small")
                },
                hide_index=True,
                use_container_width=True,
                height=500
            )
        else:
            st.warning("조건에 부합하는 타겟 기사가 없습니다.")

    with tab2:
        if not st.session_state['df_f'].empty:
            st.dataframe(
                st.session_state['df_f'],
                column_config={
                    "발행일": st.column_config.TextColumn("Time", width="small"),
                    "제목": st.column_config.TextColumn("Headline", width="large"),
                    "기사링크": st.column_config.LinkColumn("Link", display_text="🔗 이동"),
                    "분류": st.column_config.TextColumn("Filter Reason", width="medium")
                },
                hide_index=True,
                use_container_width=True,
                height=500
            )
        else:
            st.info("차단된 기사가 없습니다.")
else:
    # 초기 상태 화면
    st.info("👈 왼쪽 제어 패널에서 조건 설정 후 **[데이터 갱신]** 버튼을 눌러주세요.")