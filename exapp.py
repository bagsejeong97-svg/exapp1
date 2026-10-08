import os
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

COMPANY_NAME = os.getenv('COMPANY_NAME', '내회사')
DAY_RATE = int(os.getenv('DEFAULT_DAY_RATE',15000))
NIGHT_RATE = int(os.getenv('DEFAULT_NIGHT_RATE', 30000))
WEEKEND_RATE = int(os.getenv('DEFAULT_WEEKEND_RATE', 50000))

st.set_page_config(
    page_title=f'{COMPANY_NAME} 월급 계산기',
    page_icon='💰',
    layout='wide'
)

st.title(f'💰💰💰 {COMPANY_NAME} 월급 계산기 (주휴수당 미포함) 💰💰💰')

# 세션 상태 초기화 (근로 기록 저장)
if 'work_records' not in st.session_state:
    st.session_state.work_records = []

# 탭 생성
tab1, tab2 = st.tabs(['급여 설정', f'{COMPANY_NAME} 급여 명세서'])

# --- Tab 1: 근무 등록 및 시급 설정 ---
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader('근무 날짜 및 종류 체크')
        with st.form("detail_input_form", clear_on_submit=True):
            c1, c2 = st.columns(2)

            with c1:
                work_date = st.date_input('근무 날짜')
                job_type = st.selectbox('근무 형태 선택', ['주간', '야간', '주말'])

            with c2:
                work_hours = st.number_input('일한 시간 (시간)', min_value=0.0, max_value=12.0, value=8.0, step=1.0)
                # .env에서 불러온 환경변수 적용
                default_rates = {
                    '주간': DAY_RATE,
                    '야간': NIGHT_RATE,
                    '주말': WEEKEND_RATE
                }
                hourly_rate = st.number_input('시급 (원)', value=default_rates[job_type], step=500)

            submitted = st.form_submit_button('근무 기록 추가')

            if submitted:
                daily_pay = int(work_hours * hourly_rate)
                st.session_state.work_records.append({
                    '날짜': work_date,
                    '근무 형태': job_type,
                    '근무 시간': work_hours,
                    '시급': hourly_rate,
                    '일당': daily_pay
                })
                st.success('저장완료')

    with col2:
        st.subheader('입력 안내')
        st.info("""
        1. 일별 근무지 작성 후 추가 부탁드립니다.\n
        2. 달별로 입력해 주시기 바랍니다.
        """)

# --- Tab 2: 내역 확인, 수정/삭제 및 최종 급여 출력 ---
with tab2:
    st.subheader(f'{COMPANY_NAME} 급여 명세서')

    if st.session_state.work_records:
        # 데이터프레임 변환
        df = pd.DataFrame(st.session_state.work_records)
        df = df.sort_values(by='날짜', ascending=True)

        # 1. 일한 날짜와 시간 내역 출력
        df_display = df.copy()
        df_display['시급'] = df_display['시급'].apply(lambda x: f"{x:,}원")
        df_display['일당'] = df_display['일당'].apply(lambda x: f"{x:,}원")
        df_display['근무 시간'] = df_display['근무 시간'].apply(lambda x: f"{x}시간")

        st.dataframe(df_display, use_container_width=True)

        st.markdown("---")

        # 2. 수정 항목이 없을 시 총 급여 확인 버튼
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            total_btn = st.button('총 급여 계산하기', type='primary')
        with col_btn2:
            if st.button('전체 기록 삭제'):
                st.session_state.work_records = []
                st.rerun()

        # 버튼 클릭 시 최종 받아야 할 돈 출력
        if total_btn:
            total_hours = df['근무 시간'].sum()
            total_salary = df['일당'].sum()

            st.success("당월 급여 명세서")

            res_c1, res_c2 = st.columns(2)
            with res_c1:
                st.metric(label="총 근무 시간", value=f"{total_hours:.1f} 시간")
            with res_c2:
                st.metric(label="이번 달 총 받아야 할 돈", value=f"{total_salary:,} 원")

    else:
        st.warning('급여설정이 되지 않았습니다.')