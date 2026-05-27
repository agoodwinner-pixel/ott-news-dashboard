import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import email.utils

# --- [디자인] 페이지 설정 ---
st.set_page_config(page_title="OTT Industry Intelligence", page_icon="📈", layout="wide")

# [디자인] 커스텀 스타일 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #1E3A8A; font-family: 'Pretendard', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# API 키 설정 (Secrets 사용)
CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]

# 필터링 단어 재정비
BLACK_LIST = ["출연", "캐스팅", "첫방", "시청률", "아이돌", "배우", "드라마", "예능", "화제", "포토", "종영", "비하인드", "팬미팅", "제작발표회", "라인업", "시즌2", "결말", "티저", "감독", "예고편", "포스터", "신작", "몇부작", "연기", "정체", "시청자", "관전포인트", "스포일러", "안방극장", "스크린", "줄거리", "회차"]
WHITE_LIST = ["합병", "인수", "지분", "실적", "공정위", "구조조정", "전략", "대표", "적자", "흑자", "매출", "투자", "MAU", "점유율", "가입자", "기업결합", "시너지", "주주", "재무", "규제", "토종", "연합", "광고", "요금제", "영입", "플랫폼", "동향", "경쟁", "무료", "생존", "이용률", "매각"]

def clean_html(text):
    text = re.sub(r'<.*?>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

def is_industry_news(title, description):
    full_text = title + " " + description
    has_black = any(word in full_text for word in BLACK_LIST)
    has_white = any(word in full_text for word in WHITE_LIST)
    if has_white: return True, "✅ 산업 핵심 뉴스"
    if not has_black: return True, "✅ 일반 정보"
    return False, "🚫 연예/홍보성 기사"

# --- [기사량 확대] 뉴스 수집 함수 ---
def fetch_all_news(query, days=4):
    target_date = (datetime.now() - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    
    valid_list, filtered_list = [], []
    
    # [핵심] 100건씩 끊어서 최대 1000건까지 확인 (페이지네이션)
    for start_index in range(1, 1001, 100):
        params = {"query": query, "display": 100, "start": start_index, "sort": "date"}
        try:
            res = requests.get(url, headers=headers, params=params).json()
            items = res.get('items', [])
            if not items: break
            
            for item in items:
                pub_date = email.utils.parsedate_to_datetime(item['pubDate']).replace(tzinfo=None)
                if pub_date < target_date:
                    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)
                
                title, desc = clean_html(item['title']), clean_html(item['description'])
                is_valid, reason = is_industry_news(title, desc)
                news_data = {
                    "발행일": pub_date.strftime("%m-%d %H:%M"),
                    "언론사": "네이버뉴스", # 필요시 추출 가능
                    "제목": title,
                    "요약": desc,
                    "기사링크": item['link'],
                    "분류": reason
                }
                if is_valid: valid_list.append(news_data)
                else: filtered_list.append(news_data)
        except:
            break
            
    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)

# --- UI 레이아웃 ---
st.title("📈 OTT Industry Intelligence")
st.markdown("국내 OTT 산업 뉴스 실시간 관제 및 정제 대시보드")

with st.sidebar:
    st.header("⚙️ Search Control")
    # 검색어 팁: "OR"를 사용하면 더 많은 기사를 가져옵니다.
    search_keyword = st.text_input("검색어 설정", value="티빙 웨이브 합병 OR 티빙 실적 OR 웨이브 매각")
    search_days = st.slider("조회 기간 (일)", 1, 14, 5)
    update_btn = st.button("🔥 실시간 데이터 수집", use_container_width=True)
    st.divider()
    st.caption("Tip: 'OR'를 사용해 여러 키워드를 넣으면 기사 수집량이 늘어납니다.")

if update_btn:
    with st.spinner('네이버 뉴스를 1,000건까지 분석 중입니다...'):
        df_v, df_f = fetch_all_news(search_keyword, search_days)
        st.session_state['df_v'] = df_v
        st.session_state['df_f'] = df_f

if 'df_v' in st.session_state:
    # 상단 지표 영역
    m1, m2, m3 = st.columns(3)
    m1.metric("수집된 유효 뉴스", f"{len(st.session_state['df_v'])} 건")
    m2.metric("필터링된 노이즈", f"{len(st.session_state['df_f'])} 건")
    m3.metric("분석 대상 기간", f"{search_days} 일")

    # 결과 테이블
    tab1, tab2 = st.tabs(["💎 선별된 산업 기사", "🗑️ 필터링된 기사"])
    
    with tab1:
        if not st.session_state['df_v'].empty:
            st.dataframe(
                st.session_state['df_v'],
                column_config={
                    "기사링크": st.column_config.LinkColumn("원문 바로가기", display_text="🔗 클릭하여 읽기"),
                    "제목": st.column_config.TextColumn("기사 제목", width="large"),
                    "발행일": st.column_config.TextColumn("날짜", width="small")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.warning("조건에 맞는 기사가 없습니다. 검색어를 확장해 보세요.")

    with tab2:
        st.dataframe(st.session_state['df_f'], use_container_width=True, hide_index=True)
else:
    st.info("👈 왼쪽 사이드바에서 [실시간 데이터 수집] 버튼을 눌러 분석을 시작하세요!")