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

# 커스텀 스타일 (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    h1 { color: #1E3A8A; font-family: 'Pretendard', sans-serif; }
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

# ==========================================
# 3. 뉴스 수집 엔진 (에러 감지 + 1,000건 확장)
# ==========================================
def fetch_all_news(query, days=4):
    target_date = (datetime.now() - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    
    valid_list, filtered_list = [], []
    
    # 100건씩 끊어서 최대 1000건까지 확인
    for start_index in range(1, 1001, 100):
        params = {"query": query, "display": 100, "start": start_index, "sort": "date"}
        try:
            res = requests.get(url, headers=headers, params=params)
            
            # API 에러 발생 시 대시보드 화면에 즉시 빨간색 경고창 표시
            if res.status_code != 200:
                st.error(f"🚨 네이버 API 에러 발생! (상태 코드: {res.status_code}) API 키 설정이나 검색어를 다시 확인해주세요.")
                break
                
            data = res.json()
            items = data.get('items', [])
            if not items: break
            
            for item in items:
                pub_date = email.utils.parsedate_to_datetime(item['pubDate']).replace(tzinfo=None)
                
                # 타겟 날짜보다 과거 기사가 나오면 즉시 함수 종료 후 결과 반환
                if pub_date < target_date:
                    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)
                
                title, desc = clean_html(item['title']), clean_html(item['description'])
                is_valid, reason = is_industry_news(title, desc)
                news_data = {
                    "발행일": pub_date.strftime("%m-%d %H:%M"),
                    "언론사": "네이버뉴스",
                    "제목": title,
                    "요약": desc,
                    "기사링크": item['link'],
                    "분류": reason
                }
                if is_valid: valid_list.append(news_data)
                else: filtered_list.append(news_data)
                
        except Exception as e:
            st.error(f"🚨 데이터 수집 중 알 수 없는 에러가 발생했습니다: {e}")
            break
            
    return pd.DataFrame(valid_list), pd.DataFrame(filtered_list)

# ==========================================
# 4. 화면(UI) 레이아웃
# ==========================================
st.title("📈 OTT Industry Intelligence")
st.markdown("국내 OTT 산업 뉴스 실시간 관제 및 정제 대시보드")

with st.sidebar:
    st.header("⚙️ Search Control")
    # [수정] 에러의 원인이었던 영단어 'OR'를 기본값에서 제거했습니다.
    search_keyword = st.text_input("검색어 설정", value="티빙 웨이브 합병")
    search_days = st.slider("조회 기간 (일)", 1, 14, 5)
    update_btn = st.button("🔥 실시간 데이터 수집", use_container_width=True)
    
    st.divider()
    st.caption("💡 **Tip:** 여러 키워드를 조합하여 기사량을 늘리려면 영어 OR 대신 **`|` (파이프 기호)**를 사용하세요. \n\n*(예시: `티빙 합병 | 웨이브 매각`)*")

# 업데이트 버튼을 눌렀을 때의 동작
if update_btn:
    with st.spinner('네이버 뉴스를 최대 1,000건까지 실시간 분석 중입니다...'):
        df_v, df_f = fetch_all_news(search_keyword, search_days)
        st.session_state['df_v'] = df_v
        st.session_state['df_f'] = df_f

# 분석 결과가 세션에 저장되어 있을 때만 화면에 출력
if 'df_v' in st.session_state:
    # 3칸으로 나뉜 지표(Metrics) 표시
    m1, m2, m3 = st.columns(3)
    m1.metric("수집된 유효 뉴스", f"{len(st.session_state['df_v'])} 건")
    m2.metric("필터링된 노이즈", f"{len(st.session_state['df_f'])} 건")
    m3.metric("분석 대상 기간", f"{search_days} 일")

    # 탭 메뉴 구성
    tab1, tab2 = st.tabs(["💎 선별된 산업 기사", "🗑️ 필터링된 기사"])
    
    with tab1:
        if not st.session_state['df_v'].empty:
            # ⭐️ 기사 링크를 클릭할 수 있는 인터랙티브 테이블 생성
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
            st.warning("해당 기간 내에 조건에 맞는 유효한 기사가 없습니다. 사이드바에서 검색어를 변경해보세요.")

    with tab2:
        if not st.session_state['df_f'].empty:
            st.dataframe(
                st.session_state['df_f'],
                column_config={
                    "기사링크": st.column_config.LinkColumn("원문 바로가기", display_text="🔗 클릭하여 읽기"),
                    "제목": st.column_config.TextColumn("기사 제목", width="medium"),
                    "분류": st.column_config.TextColumn("차단 사유", width="medium")
                },
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("필터링된 연예/노이즈 기사가 없습니다.")
else:
    st.info("👈 왼쪽 사이드바에서 **[🔥 실시간 데이터 수집]** 버튼을 눌러 분석을 시작하세요!")