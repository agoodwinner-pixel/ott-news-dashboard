import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import email.utils

# ==========================================
# 1. 디자인 및 페이지 설정
# ==========================================
st.set_page_config(page_title="OTT Industry Intelligence", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    h1 { color: #1E3A8A; font-size: 2rem !important; font-family: 'Pretendard', sans-serif; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. API 키 및 필터링 설정
# ==========================================
try:
    CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]
except Exception as e:
    st.error("🚨 Secrets 설정이 누락되었습니다. Streamlit Cloud 설정(Advanced settings)에서 API 키를 입력해주세요.")
    st.stop()

# 필터링 단어 사전
BLACK_LIST = ["출연", "캐스팅", "첫방", "시청률", "아이돌", "배우", "드라마", "예능", "화제", "포토", "종영", "비하인드", "팬미팅", "제작발표회", "라인업", "시즌2", "결말", "티저", "감독", "예고편", "포스터", "신작", "몇부작", "연기", "정체", "시청자", "관전포인트", "스포일러", "안방극장", "스크린", "줄거리", "회차"]
WHITE_LIST = ["인수", "지분", "실적", "공정위", "구조조정", "전략", "대표", "적자", "흑자", "매출", "투자", "MAU", "점유율", "가입자", "기업결합", "시너지", "주주", "재무", "규제", "토종", "연합", "광고", "요금제", "영입", "플랫폼", "동향", "경쟁", "무료", "생존", "이용률", "매각", "합병"]

def clean_html(text):
    text = re.sub(r'<.*?>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

def is_industry_news(title, description):
    full_text = title + " " + description
    has_black = any(word in full_text for word in BLACK_LIST)
    has_white = any(word in full_text for word in WHITE_LIST)
    
    # Opt-in 방식 필터링
    if has_white: 
        if has_black:
            return True, "✅ 통과 (블랙+화이트 혼합)"
        return True, "✅ 통과 (산업 뉴스)"
        
    if has_black: 
        return False, "🚫 차단 (연예/홍보 단어)"
        
    return False, "🚫 차단 (산업 관련 단어 없음)"

# ==========================================
# 3. 뉴스 수집 엔진
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
                st.error(f"🚨 네이버 API 에러 발생! (코드: {res.status_code})")
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
                    "분류사유": reason
                }
                if is_valid: valid_list.append(news_data)
                else: filtered_list.append(news_data)
                
        except Exception as e:
            st.error(f"🚨 에러 발생: {e}")
            break
            
    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)

# ==========================================
# 4. 레이아웃 및 대시보드 구성
# ==========================================
st.title("📈 OTT Industry Intelligence")

with st.sidebar:
    st.header("⚙️ Control")
    
    # 🚨 [수정됨] 필터링이 일하는 것을 보기 위해 기본 검색어에서 "합병"을 뺐습니다!
    search_keyword = st.text_input("검색어 설정", value="티빙 웨이브")
    search_days = st.slider("조회 기간 (일)", 1, 7, 5)
    
    update_btn = st.button("🔥 데이터 업데이트", use_container_width=True)
    
    st.divider()
    
    # 🚨 [추가됨] 블랙리스트/화이트리스트 확인 기능 (접었다 폈다 할 수 있는 Expander)
    with st.expander("📝 현재 필터링 단어장 보기"):
        st.markdown("**🟢 화이트리스트 (반드시 포함)**")
        st.caption(", ".join(WHITE_LIST))
        st.markdown("**🔴 블랙리스트 (연예/콘텐츠)**")
        st.caption(", ".join(BLACK_LIST))
        
    st.caption("복합 검색 시 `|` 기호를 사용하세요. \n*(예: `티빙 합병 | 웨이브 매각`)*")

if update_btn:
    with st.spinner('실시간 분석 중...'):
        df_v, df_f = fetch_all_news(search_keyword, search_days)
        st.session_state['df_v'] = df_v
        st.session_state['df_f'] = df_f

if 'df_v' in st.session_state:
    m1, m2, m3 = st.columns(3)
    m1.metric("선별된 산업 기사", f"{len(st.session_state['df_v'])} 건")
    m2.metric("차단된 노이즈 기사", f"{len(st.session_state['df_f'])} 건")
    m3.metric("조회 기간", f"{search_days} 일간")

    tab1, tab2 = st.tabs(["💎 산업 기사 목록", "🗑️ 차단된 기사 목록"])
    
    with tab1:
        if not st.session_state['df_v'].empty:
            st.dataframe(
                st.session_state['df_v'],
                column_config={
                    "발행일": st.column_config.TextColumn("발행일", width="small"),
                    "제목": st.column_config.TextColumn("기사 제목", width="large"),
                    "기사링크": st.column_config.LinkColumn("링크", display_text="🔗 원문보기"),
                    "분류사유": st.column_config.TextColumn("분류", width="small")
                },
                hide_index=True,
                use_container_width=True,
                height=450 
            )
        else:
            st.warning("조건에 맞는 기사가 없습니다.")

    with tab2:
        if not st.session_state['df_f'].empty:
            st.dataframe(
                st.session_state['df_f'],
                column_config={
                    "발행일": st.column_config.TextColumn("발행일", width="small"),
                    "제목": st.column_config.TextColumn("기사 제목", width="large"),
                    "기사링크": st.column_config.LinkColumn("링크", display_text="🔗 원문보기"),
                    "분류사유": st.column_config.TextColumn("차단 사유", width="small")
                },
                hide_index=True,
                use_container_width=True,
                height=450
            )
        else:
            st.info("차단된 기사가 없습니다.")
else:
    st.info("👈 왼쪽에서 **[🔥 데이터 업데이트]** 버튼을 누르면 한눈에 보는 대시보드가 활성화됩니다.")