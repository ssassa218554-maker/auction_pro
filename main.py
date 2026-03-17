import streamlit as st
from datetime import datetime

# 1. 페이지 설정 (아이폰/PC 최적화)
st.set_page_config(page_title="부동산 경매 분석기", layout="centered")

# --- 커스텀 스타일 (디자인 업그레이드) ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; border: none; }
    .result-card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }
    .metric-title { font-size: 14px; color: #6c757d; margin-bottom: 5px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #212529; }
    .warning-card { background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; border-radius: 8px; }
    .danger-card { background-color: #f8d7da; border-left: 5px solid #dc3545; padding: 15px; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏙️ 서울 아파트 경매 분석")

# --- [입력 섹션] ---
with st.expander("📝 물건 정보 입력 (여기를 눌러서 입력하세요)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        case_no = st.text_input("사건번호", value="2024타경 ")
        apt_name = st.text_input("아파트명 (예: 잠실 엘스)")
        address = st.text_input("상세 주소(구/동)")
    with col2:
        build_year = st.number_input("준공 연도", value=2010, step=1)
        curr_floor = st.number_input("해당 층", value=10, step=1)
        total_floor = st.number_input("전체 층", value=20, step=1)
        area = st.number_input("전용면적(m²)", value=84.0)

    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        appraisal_price = st.number_input("감정가 (원)", value=1000000000, step=10000000)
        min_bid_price = st.number_input("최저가 (원)", value=800000000, step=10000000)
    with col4:
        my_bid_price = st.number_input("나의 예상 낙찰가 (원)", value=900000000, step=10000000)
        market_price = st.number_input("현재 급매 시세 (원)", value=1100000000, step=10000000)

    caution_text = st.text_area("매각물건명세서/주의사항 복사", height=100, placeholder="대항력, 유치권 등 서류 내용을 여기에 붙여넣으세요.")

# --- [분석 로직] ---
curr_year = datetime.now().year
apt_age = curr_year - build_year
acquisition_tax = my_bid_price * 0.011 # 기본 취득세 1.1%
total_investment = my_bid_price + acquisition_tax + (area * 30000) # 수리비 보수적 계산
expected_profit = market_price - total_investment

# --- [결과 출력 섹션] ---
if apt_name:
    st.divider()
    st.subheader(f"📊 {apt_name} 분석 결과")

    # 1. 핵심 수익성 지표
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""<div class='result-card'>
            <div class='metric-title'>💰 예상 순수익</div>
            <div class='metric-value'>{expected_profit:,.0f}원</div>
            <small>취득세/수리비 등 부대비용 제외</small>
        </div>""", unsafe_allow_html=True)
    with col_res2:
        profit_rate = (expected_profit / total_investment) * 100
        st.markdown(f"""<div class='result-card'>
            <div class='metric-title'>📈 수익률</div>
            <div class='metric-value'>{profit_rate:.1f}%</div>
            <small>투자금액 대비 수익 비율</small>
        </div>""", unsafe_allow_html=True)

    # 2. 리스크 분석
    danger_keywords = ["대항력", "임차인", "미납", "유치권", "인수", "주의"]
    found_keywords = [word for word in danger_keywords if word in caution_text]

    if found_keywords or apt_age >= 20 or curr_floor <= 3:
        st.markdown("### ⚠️ 체크 포인트")
        
        if found_keywords:
            st.markdown(f"""<div class='danger-card'>
                <strong>[권리 분석 경고]</strong> {', '.join(found_keywords)} 키워드가 발견되었습니다. 법원 서류를 정밀 검토하세요.
            </div>""", unsafe_allow_html=True)
            st.write("")

        if apt_age >= 20:
            st.markdown(f"""<div class='warning-card'>
                <strong>[노후도 주의]</strong> {apt_age}년차 구축입니다. 대규모 수리비 발생 가능성이 높습니다.
            </div>""", unsafe_allow_html=True)
            st.write("")

        if curr_floor <= 3:
            st.markdown(f"""<div class='warning-card'>
                <strong>[층수 감가]</strong> {curr_floor}층 저층 물건입니다. 인근 저층 실거래가를 기준으로 다시 산정하세요.
            </div>""", unsafe_allow_html=True)

    # 3. 상세 리포트
    with st.expander("📍 물건 요약 리포트"):
        st.write(f"- **위치:** {address}")
        st.write(f"- **연식:** {build_year}년 준공 ({apt_age}년차)")
        st.write(f"- **층수:** {total_floor}층 중 {curr_floor}층")
        st.write(f"- **총 투자비:** 약 {total_investment:,.0f}원 (낙찰가+세금+기본수리)")

else:
    st.info("좌측 상단에서 아파트명을 입력하면 상세 분석 결과가 나타납니다.")
    