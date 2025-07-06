import streamlit as st

st.title("🌌 나만의 Streamlit 앱")
st.write("안녕하세요! 이 앱은 GitHub와 Streamlit을 활용해 만든 기본 예제입니다.")

# 사용자 입력
name = st.text_input("당신의 이름을 입력하세요:")
if name:
    st.success(f"{name}님, 반갑습니다! 🎉")

# 버튼 예제
if st.button("오늘 날짜 보기"):
    from datetime import datetime
    st.info(f"📅 오늘은 {datetime.now().strftime('%Y-%m-%d')}입니다.")
