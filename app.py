import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import email.utils

# 페이지 설정
st.set_page_config(page_title="OTT 산업 뉴스 센터", layout="wide")

# 1. API 키 설정 (Streamlit Secrets 사용)
# 로컬 테스트 시에는 st.secrets 대신 직접 문자열을 넣어도 되지만, 배포 시에는 Secrets 설정을 권장합니다.
CLIENT_ID = st.secrets["NAVER_CLIENT_ID"]
CLIENT_SECRET = st.secrets["NAVER_CLIENT_SECRET"]

# --- 필터링 로직 ---
BLACK_LIST = ["출연", "캐스팅", "첫방", "시청률", "아이돌", "배우", "드라마", "예능", "화제", "포토", "종영", "비하인드", "팬미팅", "제작발표회", "라인업", "시즌2", "결말", "티저", "감독", "예고편", "포스터", "신작", "몇부작", "연기", "정체", "시청자", "관전포인트", "스포일러", "안방극장", "스크린", "줄거리", "회차"]
WHITE_LIST = ["규제", "토종", "연합", "광고", "요금제", "영입", "플랫폼", "동향", "경쟁", "무료", "생존", "이용률", "매각", "CPO", "CEO", "인수", "지분", "실적", "공정위", "구조조정", "전략", "대표", "적자", "흑자", "매출", "투자", "MAU", "점유율", "가입자", "기업결합", "시너지", "주주", "재무"]

def clean_html(text):
    text = re.sub(r'<.*?>', '', text)
    return text.replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&')

def is_industry_news(title, description):
    full_text = title + " " + description
    has_black = any(word in full_text for word in BLACK_LIST)
    has_white = any(word in full_text for word in WHITE_LIST)
    if has_white: return True, "✅ 통과 (산업 핵심어 포함)"
    if has_black: return False, "🚫 차단됨 (연예/홍보 단어)"
    return False, "🚫 차단됨 (산업 관련 단어 없음)"

# --- 뉴스 수집 함수 ---
def fetch_news(query, days=4):
    target_date = (datetime.now() - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    
    valid_list, filtered_list = [], []
    start = 1
    
    while start <= 500: # 최대 500건까지 확인
        params = {"query": query, "display": 100, "start": start, "sort": "date"}
        res = requests.get(url, headers=headers, params=params).json()
        items = res.get('items', [])
        if not items: break
        
        for item in items:
            pub_date = email.utils.parsedate_to_datetime(item['pubDate']).replace(tzinfo=None)
            if pub_date < target_date:
                start = 9999 # 루프 종료
                break
            
            title, desc = clean_html(item['title']), clean_html(item['description'])
            is_valid, reason = is_industry_news(title, desc)
            data = {"제목": title, "요약": desc, "발행일": pub_date.strftime("%Y-%m-%d %H:%M"), "링크": item['link'], "사유": reason}
            
            if is_valid: valid_list.append(data)
            else: filtered_list.append(data)
        start += 100
    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)

# --- UI 레이아웃 ---
st.title("🚀 OTT 산업 뉴스 관제 센터")
st.sidebar.header("🔍 검색 설정")
keyword = st.sidebar.text_input("검색어", value="티빙 웨이브 합병 OTT")
days_ago = st.sidebar.slider("검색 기간 (일)", 1, 7, 4)

if st.sidebar.button("지금 뉴스 업데이트"):
    df_v, df_f = fetch_news(keyword, days_ago)
    st.session_state['df_v'] = df_v
    st.session_state['df_f'] = df_f

if 'df_v' in st.session_state:
    col1, col2 = st.columns(2)
    col1.metric("산업 뉴스", f"{len(st.session_state['df_v'])} 건")
    col2.metric("차단된 노이즈", f"{len(st.session_state['df_f'])} 건")
    
    tab1, tab2 = st.tabs(["🟢 정제된 뉴스", "🔴 필터링된 기사"])
    with tab1:
        st.dataframe(st.session_state['df_v'], use_container_width=True)
    with tab2:
        st.dataframe(st.session_state['df_f'], use_container_width=True)
else:
    st.info("왼쪽 사이드바의 [지금 뉴스 업데이트] 버튼을 눌러주세요.")