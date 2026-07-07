import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg') # 브라우저 충돌 방지용 필수 설정
import matplotlib.pyplot as plt

# =================================================================
# 1. 웹페이지 기본 설정
# =================================================================
st.set_page_config(layout="wide")
st.title("🧪 차세대 환경 신소재 스마트 센서 모니터링 시스템")
st.write("MBL 중화적정 메커니즘을 이용한 신소재별 pH 오염 감지 시뮬레이터입니다.")
st.markdown("---")

# =================================================================
# 2. 왼쪽 제어 패널 인터페이스 (사이드바)
# =================================================================
st.sidebar.header("🛠️ 센서 및 환경 변수 설정")

MATERIAL_CHOICE = st.sidebar.radio(
    "실험 및 분석할 환경 신소재 선택",
    ("PVA-흑연 복합체", "Alginate-CNT (알긴산-탄소나노튜브)")
)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 pH 환경 및 적정 곡선 설정")

INITIAL_PH = st.sidebar.slider("초기 산도 (Initial pH)", min_value=0.0, max_value=7.0, value=2.0, step=0.1)
FINAL_PH = st.sidebar.slider("최종 산도 (Final pH)", min_value=7.0, max_value=14.0, value=12.0, step=0.1)
EQUIVALENCE_TIME = st.sidebar.slider("중화(오염 유입) 타이밍 (초)", min_value=10.0, max_value=90.0, value=50.0, step=1.0)
SLOPE_SHARPNESS = st.sidebar.slider("반응 급격도 (곡선 기울기)", min_value=1.0, max_value=10.0, value=3.0, step=0.5)


# =================================================================
# 3. 수학적 데이터 생성 및 센서 알고리즘 연산
# =================================================================
time = np.linspace(0, 100, 200) # X축 데이터 (0~100초)
ph_range = FINAL_PH - INITIAL_PH
# 사용자가 지정한 슬라이더 값에 맞춘 Y축 pH 데이터
pH_data = INITIAL_PH + (ph_range / (1 + np.exp(-(time - EQUIVALENCE_TIME) / SLOPE_SHARPNESS)))

# 변화율(미분) 계산
base_signal = np.gradient(pH_data, time)

# 선택한 소재에 따른 센서 고유 신호 정의
if MATERIAL_CHOICE == "PVA-흑연 복합체":
    np.random.seed(42)
    noise = np.random.normal(0, 0.02, size=len(time))
    sensor_signal = base_signal * 1.0 + noise
    material_desc = "PVA의 수산기(-OH) 수축과 흑연 입자 간 거리 변화를 이용한 전도성 센서입니다. 가성비가 좋고 질깁니다."
    color_theme = "#00BFFF" # 하늘색
else:
    sensor_signal = base_signal * 1.5 
    material_desc = "친환경 해조류 추출 알긴산(-COOH) 고분자와 튜브형 탄소나노튜브를 결합하여, 미세한 pH 변화도 매우 정밀하고 강력하게 잡아내는 고감도 센서입니다."
    color_theme = "#32CD32" # 라임그린

# 최대 피크(당량점) 시점 자동 연산
max_idx = np.argmax(sensor_signal)
detect_time = time[max_idx]
detect_pH = pH_data[max_idx]
detect_intensity = sensor_signal[max_idx]


# =================================================================
# 4. 메인 대시보드 화면 구성 (Matplotlib 완전 안정화 버전)
# =================================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 실시간 데이터 시각화")
    
    # 맷플롯립 도화지 켜기 (오류 방지를 위해 함수 내부에서 깨끗하게 새로 생성)
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))

    # [좌측 그래프] pH 변화 모니터 (순수 넘파이 배열 주입으로 오류 원천 차단)
    ax[0].plot(time, pH_data, color="#FFD700", linewidth=3, label="Environmental pH")
    ax[0].axvline(x=detect_time, color="red", linestyle=":", alpha=0.7)
    ax[0].set_title("1. Real-time pH Monitor")
    ax[0].set_xlabel("Time (seconds)")
    ax[0].set_ylabel("pH Level")
    ax[0].set_ylim(-0.5, 14.5)
    ax[0].grid(True, linestyle="--", alpha=0.5)
    ax[0].legend()

    # [우측 그래프] 신소재 센서 출력 신호
    ax[1].plot(time, sensor_signal, color=color_theme, linewidth=2.5, label="Sensor Output")
    ax[1].scatter(detect_time, detect_intensity, color="crimson", s=120, zorder=5, label="Max Peak")
    ax[1].axvline(x=detect_time, color="crimson", linestyle="--", alpha=0.7)
    ax[1].set_title(f"2. {MATERIAL_CHOICE} Signal (dR/dt)")
    ax[1].set_xlabel("Time (seconds)")
    ax[1].set_ylabel("Signal Intensity")
    ax[1].grid(True, linestyle="--", alpha=0.5)
    ax[1].legend()

    # 스트림릿 웹 화면에 도화지 강제 출력 (fig를 명시하여 렌더링 누락 방지)
    st.pyplot(fig)

with col2:
    st.subheader("📋 스마트 센서 자동 진단 보고서")
    
    # 스코어보드 출력
    st.metric(label="💡 감지된 오염 유입 시점", value=f"{detect_time:.2f} 초")
    st.metric(label="🧪 피크 시점의 수용액 산도", value=f"pH {detect_pH:.2f}")
    st.metric(label="⚡ 센서 최대 신호 강도", value=f"{detect_intensity:.4f}")
    
    st.success(f"**[현재 가동 중인 소재]**\n\n{MATERIAL_CHOICE}")
    st.markdown("### 🔍 신소재 공학적 특성")
    st.caption(material_desc)