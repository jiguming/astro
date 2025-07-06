import streamlit as st
from astropy.io import fits
from astropy.wcs import WCS
import numpy as np
from PIL import Image
import io

# --- Helper Functions ---

def process_fits_image(uploaded_file):
    """
    업로드된 FITS 파일 처리
    """
    if uploaded_file is not None:
        try:
            # 파일을 메모리에서 직접 읽기
            hdul = fits.open(uploaded_file)
            hdu = hdul[0]  # 기본 HDU 사용
            wcs = WCS(hdu.header)
            data = hdu.data
            hdul.close()
            return data, wcs, hdu.header
        except Exception as e:
            st.error(f"FITS 파일 처리 중 오류 발생: {e}")
            return None, None, None
    return None, None, None

def normalize_data(data):
    """
    시각화를 위해 데이터 정규화 (0-255 스케일)
    """
    # NaN 값이나 무한대 값을 0으로 처리
    data = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
    # 데이터 스케일링
    min_val = np.min(data)
    max_val = np.max(data)
    if max_val == min_val:
        return np.zeros(data.shape, dtype=np.uint8)
    # 정규화
    normalized_data = 255 * (data - min_val) / (max_val - min_val)
    return normalized_data.astype(np.uint8)

# --- Streamlit App ---

st.set_page_config(page_title="천문 이미지 물리량 분석기", layout="wide")

st.title("🔭 천문 이미지 물리량 처리 앱")
st.markdown("""
이 앱은 FITS 형식의 천문 이미지를 업로드하여 기본적인 물리량을 분석하는 도구입니다.
**GitHub**와 **Streamlit**을 사용하여 제작되었습니다.
""")

# --- 1. 파일 업로드 ---
st.header("1. FITS 파일 업로드")
uploaded_file = st.file_uploader("분석할 FITS 파일을 선택하세요.", type=['fits', 'fit'])

if uploaded_file:
    # 세션 상태에 데이터 저장
    if 'fits_data' not in st.session_state or st.session_state.get('file_name') != uploaded_file.name:
        st.session_state.fits_data, st.session_state.wcs, st.session_state.header = process_fits_image(uploaded_file)
        st.session_state.file_name = uploaded_file.name

    if st.session_state.fits_data is not None:
        st.success(f"'{uploaded_file.name}' 파일이 성공적으로 업로드되었습니다.")

        data = st.session_state.fits_data
        header = st.session_state.header

        # --- 2. 이미지 정보 표시 ---
        st.header("2. 이미지 정보")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("기본 정보")
            st.text(f"이미지 크기: {data.shape[1]} x {data.shape[0]} 픽셀")
            if 'OBJECT' in header:
                st.text(f"관측 대상: {header['OBJECT']}")
            if 'TELESCOP' in header:
                st.text(f"망원경: {header['TELESCOP']}")
            if 'EXPTIME' in header:
                st.text(f"노출 시간: {header['EXPTIME']} 초")

        with col2:
            st.subheader("FITS 헤더")
            # 스크롤 가능한 텍스트 영역에 헤더 정보 표시
            header_str = repr(header)
            st.text_area("전체 헤더 정보", header_str, height=200)


        # --- 3. 이미지 시각화 및 물리량 계산 ---
        st.header("3. 이미지 시각화 및 분석")

        # 이미지 시각화
        st.subheader("천문 이미지")
        img_data_normalized = normalize_data(data)
        img = Image.fromarray(img_data_normalized)
        st.image(img, caption="업로드된 FITS 이미지", use_column_width=True)

        # 물리량 계산
        st.subheader("물리량 계산")
        st.info("이미지 전체 또는 특정 영역의 평균 밝기를 계산합니다.")

        # 계산 옵션
        calc_option = st.radio("계산할 영역을 선택하세요:", ('이미지 전체', '영역 선택'))

        if calc_option == '이미지 전체':
            mean_brightness = np.mean(data)
            st.metric(label="이미지 전체 평균 밝기 (Mean Brightness)", value=f"{mean_brightness:.2f}")

        else: # 영역 선택
            st.warning("영역 선택 기능은 현재 개발 중입니다. 우선 전체 평균값만 제공됩니다.")
            # 향후 streamlit-drawable-canvas 와 같은 라이브러리를 사용하여 영역 선택 기능 추가 가능
            # 예:
            # from streamlit_drawable_canvas import st_canvas
            # canvas_result = st_canvas(...)
            # if canvas_result.json_data is not None:
            #     ... (선택 영역 좌표를 받아 해당 영역만 계산)

else:
    st.info("시작하려면 FITS 파일을 업로드해주세요.")

st.sidebar.header("앱 정보")
st.sidebar.markdown("""
- **개발자**: Gemini (AI)
- **목적**: 천문 이미지 데이터 처리 데모
- **라이브러리**: Streamlit, Astropy, NumPy, Pillow
""")
