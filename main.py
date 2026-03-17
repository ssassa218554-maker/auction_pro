import streamlit as st
from datetime import datetime

# 1. 페이지 설정 (아이폰 최적화)
st.set_page_config(page_title="경매 분석 비서", layout="centered")

st.title("🏠 서울 아파트 경매 분석기")
st.caption("아빠의 성공적인 낙찰을 응원합니다!")

# --- 입력 섹션 ---
st.subheader("📍 물건 기본 정보")
col1, col2 = st.columns(2)
with col1:
    case_no = st.text_input("사건번호", value="2024타경 ")
    apt_name = st.text_input("아파트명")
with col2:
    address = st.text_input("상세 주소(구/동)")
    area = st.number_input("전용면적(m²)", value=84.0)

col3, col4 = st.columns(2)
with col3:
    curr_floor = st.number_input("현재 층", value=1, step=1)
    build_year = st.number_input("준공 연도", value=2010, step=1)
with col4:
    total_floor = st.number_input("전체 층", value=20, step=1)
    
# --- 가격 정보 ---
st.divider()
st.subheader("💰 가격 및 수익 분석")
appraisal_price = st.number_input("감정가 (원)", value=1000000000, step=10000000)
min_bid_price = st.number_input("최저가 (원)", value=800000000, step=10000000)
my_bid_price = st.number_input("나의 예상 낙찰가 (원)", value=900000000, step=10000000)
market_price = st.number_input("현재 급매 시세 (원)", value=1100000000, step=10000000)

# --- 권리 분석 ---
st.divider()
st.subheader("🔍 권리 분석 (텍스트 붙여넣기)")
caution_text = st.text_area("매각물건명세서 등 주의사항을 복사해 넣으세요", height=150)

# --- 분석 로직 ---
st.divider()
st.subheader("📊 최종 분석 결과")

# 1. 권리 분석 경고
danger_keywords = ["대항력", "임차인", "미납", "유치권", "인수", "주의"]
found_keywords = [word for word in danger_keywords if word in caution_text]

if found_keywords:
    st.error(f"⚠️ 위험 키워드 발견: {', '.join(found_keywords)}")
    st.warning("위 키워드가 포함되어 있습니다. 반드시 법원 서류를 재확인하세요!")
else:
    st.success("✅ 특이사항 없음 (입력된 텍스트 기준)")

# 2. 층수 및 연식 분석
curr_year = datetime.now().year
apt_age = curr_year - build_year

if apt_age >= 15:
    st.info(f"💡 연식 {apt_age}년차: 배관 및 내부 수리비(평당 150만)를 예산에 반영하세요.")

if curr_floor <= 3:
    st.warning("低 저층: 시세 대비 5~10% 낮게 입찰가를 잡는 것이 좋습니다.")
elif curr_floor == total_floor:
    st.warning("高 탑층: 층간소음은 없으나 결로/누수 여부를 확인하세요.")

# 3. 수익 계산
acquisition_tax = my_bid_price * 0.011 # 기본 취득세 1.1% 가정
total_investment = my_bid_price + acquisition_tax + (area * 30000) # 수리비 대략 포함
expected_profit = market_price - total_investment

st.metric("예상 순수익", f"{expected_profit:,.0f} 원")
st.write(f"*(낙찰가 + 취득세 + 수리비 등 약 {total_investment:,.0f}원 투입 기준)*")

# 아이폰 홈 화면 추가 안내
st.sidebar.info("아이폰 Safari에서 '홈 화면에 추가'를 누르면 앱처럼 쓸 수 있습니다.")
