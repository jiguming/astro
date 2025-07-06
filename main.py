import streamlit as st
import numpy as np
from astropy.io import fits
from PIL import Image

# --- Streamlit 앱 페이지 설정 ---
st.set_page_config(page_title="천문 이미지 분석기", layout="wide")
st.title("🔭 천문 이미지 물리량 처리 앱")

# --- 파일 업로더 ('.fz' 확장자 포함) ---
uploaded_file = st.file_uploader(
    "분석할 FITS 파일을 선택하세요.",
    type=['fits', 'fit', 'fz']  # .fz 확장자 지원 추가
)

# --- 파일이 업로드 되면 실행될 로직 ---
if uploaded_file:
    try:
        # FITS 파일 열기 (압축 해제는 astropy가 자동으로 처리)
        with fits.open(uploaded_file) as hdul:
            header = hdul[0].header
            data = hdul[0].data

            # 유효하지 않은 숫자(NaN) 값을 0으로 대체
            data = np.nan_to_num(data)

            st.success(f"**'{uploaded_file.name}'** 파일을 성공적으로 처리했습니다.")

            # --- 2개 컬럼으로 레이아웃 분할 ---
            col1, col2 = st.columns(2)

            with col1:
                # --- 1. 기본 정보 표시 ---
                st.header("이미지 정보")
                st.text(f"크기: {data.shape[1]} x {data.shape[0]} 픽셀")
                if 'OBJECT' in header:
                    st.text(f"관측 대상: {header['OBJECT']}")
                if 'EXPTIME' in header:
                    st.text(f"노출 시간: {header['EXPTIME']} 초")

                # --- 2. 물리량 계산 및 표시 ---
                st.header("물리량")
                mean_brightness = np.mean(data)
                st.metric(label="이미지 전체 평균 밝기", value=f"{mean_brightness:.2f}")

            with col2:
                # --- 3. 이미지 미리보기 ---
                st.header("이미지 미리보기")
                
                # 시각화를 위해 데이터 값을 0-255 범위로 정규화
                if data.max() == data.min():
                    norm_data = np.zeros(data.shape, dtype=np.uint8)
                else:
                    scale_min = np.percentile(data, 5)  # 배경 노이즈를 고려하여 하위 5%
                    scale_max = np.percentile(data, 99.5) # 밝은 별이 과포화되는 것을 방지
                    data_clipped = np.clip(data, scale_min, scale_max)
                    
                    norm_data = (255 * (data_clipped - scale_min) / (scale_max - scale_min)).astype(np.uint8)
                
                # Pillow 라이브러리를 사용해 이미지로 변환 후 출력
                img = Image.fromarray(norm_data)
                st.image(img, caption="업로드된 FITS 이미지", use_column_width=True)

    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {e}")
        st.warning("파일이 손상되었거나 유효한 FITS 형식이 아닐 수 있습니다.")

else:
    st.info("시작하려면 FITS 파일을 업로드해주세요.")
