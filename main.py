import streamlit as st
import numpy as np
from astropy.io import fits
from PIL import Image

st.set_page_config(page_title="천문 이미지 분석기", layout="wide")
st.title("🔭 천문 이미지 물리량 처리 앱")

# 파일 업로더
uploaded_file = st.file_uploader(
    "분석할 FITS 파일을 선택하세요.",
    type=['fits', 'fit']
)

if uploaded_file:
    try:
        # FITS 파일 열기
        with fits.open(uploaded_file) as hdul:
            header = hdul[0].header
            data = hdul[0].data

            # NaN 값을 0으로 대체
            data = np.nan_to_num(data)

            st.success(f"**'{uploaded_file.name}'** 파일을 성공적으로 처리했습니다.")

            # --- 1. 정보 및 이미지 표시 ---
            col1, col2 = st.columns(2)

            with col1:
                st.header("이미지 정보")
                st.text(f"크기: {data.shape[1]} x {data.shape[0]} 픽셀")
                if 'OBJECT' in header:
                    st.text(f"관측 대상: {header['OBJECT']}")
                if 'EXPTIME' in header:
                    st.text(f"노출 시간: {header['EXPTIME']} 초")

                # 물리량 계산 및 표시
                st.header("물리량")
                mean_brightness = np.mean(data)
                st.metric(label="이미지 전체 평균 밝기", value=f"{mean_brightness:.2f}")


            with col2:
                st.header("이미지 미리보기")
                # 시각화를 위해 데이터 정규화 (0-255)
                if data.max() == data.min():
                    norm_data = np.zeros(data.shape, dtype=np.uint8)
                else:
                    norm_data = (255 * (data - data.min()) / (data.max() - data.min())).astype(np.uint8)
                
                img = Image.fromarray(norm_data)
                st.image(img, caption="업로드된 FITS 이미지", use_column_width=True)

    except Exception as e:
        st.error(f"파일 처리 중 오류 발생: {e}")

else:
    st.info("시작하려면 FITS 파일을 업로드해주세요.")
