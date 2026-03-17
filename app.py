import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

import streamlit as st


@dataclass
class AuctionInputs:
    case_number: str
    apt_name: str
    address: str
    floor_current: int
    floor_total: int
    area_m2: float
    built_year: int
    appraisal_price: int
    min_price: int
    expected_bid_price: int
    quick_sale_price: int
    eviction_and_repair_cost: int


def _format_krw(value: int) -> str:
    return f"{value:,}원"


def _safe_int(text: str) -> Optional[int]:
    if text is None:
        return None
    s = re.sub(r"[^\d]", "", str(text))
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _parse_floor_pair(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Accepts inputs like:
      - "10/25"
      - "10 / 25"
      - "10층/25층"
      - "10,25"
    """
    if not text:
        return None, None

    cleaned = (
        str(text)
        .replace("층", "")
        .replace("\\", "/")
        .replace(",", "/")
        .replace(" ", "")
    )
    if "/" not in cleaned:
        a = _safe_int(cleaned)
        return a, None
    left, right = cleaned.split("/", 1)
    return _safe_int(left), _safe_int(right)


def _find_risk_keywords(text: str) -> list[str]:
    keywords = ["대항력", "임차인", "미납", "유치권", "인수"]
    found = []
    if not text:
        return found
    for k in keywords:
        if k in text:
            found.append(k)
    return found


def _calc_property_age(built_year: int) -> int:
    now_year = datetime.now().year
    return max(0, now_year - built_year)


def _calc_acquisition_tax(bid_price: int) -> int:
    return int(round(bid_price * 0.011))


def _calc_profit(
    quick_sale_price: int, bid_price: int, eviction_and_repair_cost: int
) -> Tuple[int, int]:
    acquisition_tax = _calc_acquisition_tax(bid_price)
    total_cost = bid_price + acquisition_tax + eviction_and_repair_cost
    profit = quick_sale_price - total_cost
    return profit, total_cost


def _floor_note(cur: int, total: int) -> Optional[str]:
    if cur <= 0 or total <= 0:
        return None
    if cur <= 3:
        return "저층 주의"
    if cur == total:
        return "탑층 주의"
    return None


def _profit_rate(profit: int, total_cost: int) -> Optional[float]:
    if total_cost <= 0:
        return None
    return (profit / total_cost) * 100.0


def _card(title: str, body_md: str, tone: str = "neutral") -> None:
    tone_map = {
        "neutral": ("#f7f7f8", "#111827"),
        "good": ("#ecfdf5", "#065f46"),
        "warn": ("#fff7ed", "#9a3412"),
        "danger": ("#fef2f2", "#991b1b"),
    }
    bg, fg = tone_map.get(tone, tone_map["neutral"])
    st.markdown(
        f"""
        <div style="
          background:{bg};
          color:{fg};
          padding:14px 14px;
          border-radius:14px;
          border:1px solid rgba(17,24,39,0.08);
          box-shadow: 0 1px 2px rgba(0,0,0,0.04);
          margin: 10px 0 12px 0;
        ">
          <div style="font-weight:700; font-size:16px; margin-bottom:8px;">{title}</div>
          <div style="font-size:14px; line-height:1.5;">{body_md}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _inject_mobile_css() -> None:
    st.markdown(
        """
        <style>
          /* Slightly larger tap targets on mobile */
          div[data-testid="stTextInput"] input,
          div[data-testid="stNumberInput"] input,
          div[data-testid="stTextArea"] textarea {
            padding: 12px 12px !important;
            border-radius: 12px !important;
          }
          /* Keep content width comfortable on mobile */
          .block-container {
            padding-top: 1rem;
            padding-bottom: 5rem;
            max-width: 820px;
          }
          /* Reduce extra vertical whitespace */
          div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stForm"]) {
            margin-top: 0.25rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="서울 아파트 경매 분석 비서",
    page_icon="🏢",
    layout="centered",
    initial_sidebar_state="collapsed",
)

_inject_mobile_css()

st.title("서울 아파트 경매 분석 비서")
st.caption("아이폰에서 한손으로 입력하고, 바로 리스크/수익을 요약해주는 간단 분석 도구")


with st.form("auction_form", clear_on_submit=False, border=False):
    st.subheader("입력")

    case_number = st.text_input("사건번호", placeholder="예: 2025타경12345")
    apt_name = st.text_input("아파트명", placeholder="예: OO아파트")
    address = st.text_input("상세 주소", placeholder="예: 서울시 OO구 OO로 00, 101동 1001호")

    floor_pair = st.text_input("층수 (현재층/전체층)", placeholder="예: 10/25 또는 10층/25층")
    floor_current, floor_total = _parse_floor_pair(floor_pair)

    area_m2 = st.number_input("전용면적 (m²)", min_value=0.0, step=0.1, value=84.0)
    built_year = st.number_input("준공연도 (연식 계산용)", min_value=1900, max_value=2100, step=1, value=2005)

    appraisal_price = st.number_input("감정가 (원)", min_value=0, step=1_000_000, value=1_000_000_000)
    min_price = st.number_input("최저가 (원)", min_value=0, step=1_000_000, value=700_000_000)
    expected_bid_price = st.number_input("예상 낙찰가 (원)", min_value=0, step=1_000_000, value=800_000_000)
    quick_sale_price = st.number_input("현재 급매가(시세) (원)", min_value=0, step=1_000_000, value=950_000_000)

    eviction_and_repair_cost = st.number_input(
        "명도비 및 수리비 (원)",
        min_value=0,
        step=500_000,
        value=20_000_000,
        help="명도비 + 도배/장판/수리/인테리어 등 추정 비용 합계",
    )

    st.subheader("권리 분석 텍스트")
    rights_text = st.text_area(
        "매각물건명세서 / 주의사항 붙여넣기",
        height=220,
        placeholder="여기에 텍스트를 붙여넣으면 위험 키워드를 탐지합니다.",
    )

    submitted = st.form_submit_button("분석하기", use_container_width=True)


if submitted:
    data = AuctionInputs(
        case_number=case_number.strip(),
        apt_name=apt_name.strip(),
        address=address.strip(),
        floor_current=int(floor_current or 0),
        floor_total=int(floor_total or 0),
        area_m2=float(area_m2),
        built_year=int(built_year),
        appraisal_price=int(appraisal_price),
        min_price=int(min_price),
        expected_bid_price=int(expected_bid_price),
        quick_sale_price=int(quick_sale_price),
        eviction_and_repair_cost=int(eviction_and_repair_cost),
    )

    st.divider()
    st.subheader("결과 요약")

    # 1) 권리 분석 키워드 경고
    found = _find_risk_keywords(rights_text)
    if found:
        _card(
            "권리 리스크 경고",
            "아래 키워드가 발견되었습니다. 원문을 다시 확인하고 인수/명도/임차관계/미납 여부를 반드시 점검하세요.<br>"
            + "<b>발견 키워드:</b> "
            + ", ".join(found),
            tone="danger",
        )
    else:
        _card(
            "권리 리스크",
            "지정 키워드(대항력, 임차인, 미납, 유치권, 인수)가 탐지되지 않았습니다. 그래도 원문 전체를 꼭 확인하세요.",
            tone="good",
        )

    # 2) 연식 계산
    age = _calc_property_age(data.built_year)
    if age >= 15:
        _card("연식", f"연식: <b>{age}년</b><br>15년 이상이므로 <b>인테리어 비용 주의</b>", tone="warn")
    else:
        _card("연식", f"연식: <b>{age}년</b>", tone="neutral")

    # 3) 층수 분석
    floor_msg = _floor_note(data.floor_current, data.floor_total)
    if floor_msg:
        _card("층수", f"{data.floor_current}/{data.floor_total}층<br><b>{floor_msg}</b>", tone="warn")
    else:
        floor_line = (
            f"{data.floor_current}/{data.floor_total}층"
            if data.floor_current and data.floor_total
            else "층수 정보가 불완전합니다 (현재층/전체층 형식 권장)"
        )
        _card("층수", floor_line, tone="neutral")

    # 4) 수익/수익률 계산
    acquisition_tax = _calc_acquisition_tax(data.expected_bid_price)
    profit, total_cost = _calc_profit(
        quick_sale_price=data.quick_sale_price,
        bid_price=data.expected_bid_price,
        eviction_and_repair_cost=data.eviction_and_repair_cost,
    )
    pr = _profit_rate(profit, total_cost)
    tone = "good" if profit >= 0 else "danger"

    profit_line = f"<b>{_format_krw(profit)}</b>"
    if pr is not None:
        profit_line += f" (수익률 {pr:.2f}%)"

    _card(
        "수익률 계산",
        "<b>공식</b>: 현재 급매가 - (낙찰가 + 취득세(1.1%) + 명도비 및 수리비)<br><br>"
        + f"- 현재 급매가: <b>{_format_krw(data.quick_sale_price)}</b><br>"
        + f"- 예상 낙찰가: <b>{_format_krw(data.expected_bid_price)}</b><br>"
        + f"- 취득세(1.1%): <b>{_format_krw(acquisition_tax)}</b><br>"
        + f"- 명도비 및 수리비: <b>{_format_krw(data.eviction_and_repair_cost)}</b><br>"
        + f"- 총투입비용: <b>{_format_krw(total_cost)}</b><br><br>"
        + f"= 예상 수익: {profit_line}",
        tone=tone,
    )

    # 5) 기본 정보 카드
    summary_bits = []
    if data.case_number:
        summary_bits.append(f"- 사건번호: <b>{data.case_number}</b>")
    if data.apt_name:
        summary_bits.append(f"- 아파트명: <b>{data.apt_name}</b>")
    if data.address:
        summary_bits.append(f"- 주소: <b>{data.address}</b>")
    summary_bits.append(f"- 전용면적: <b>{data.area_m2:.1f} m²</b>")
    summary_bits.append(f"- 감정가/최저가: <b>{_format_krw(data.appraisal_price)}</b> / <b>{_format_krw(data.min_price)}</b>")

    _card("기본 정보", "<br>".join(summary_bits), tone="neutral")

else:
    st.info("위 항목을 입력한 뒤 **분석하기**를 누르면 카드 형태로 결과가 정리됩니다.")
