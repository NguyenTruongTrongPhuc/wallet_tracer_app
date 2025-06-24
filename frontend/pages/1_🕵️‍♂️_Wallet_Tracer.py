import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# --- SỬA LỖI Ở ĐÂY ---
# Thêm thư mục gốc 'frontend' vào Python Path để có thể import tuyệt đối
# Thao tác này giúp Python tìm thấy các module như 'api' và 'components'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Bây giờ chúng ta có thể sử dụng import tuyệt đối từ thư mục 'frontend'
from api import client
from components import charts

st.set_page_config(page_title="Wallet Tracer", layout="wide")

st.title("🕵️‍♂️ Công cụ Truy vết & Phân tích Ví Chuyên sâu")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Bảng điều khiển")
    with st.form(key="input_form"):
        wallet_address = st.text_input("📍 Địa chỉ ví Bitcoin", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh")
        
        today = datetime.now()
        date_range = st.date_input(
            "🗓️ Khoảng thời gian",
            (today - timedelta(days=365), today),
            min_value=datetime(2009, 1, 3),
            max_value=today
        )
        
        submitted = st.form_submit_button("🔍 Truy vết ngay")

# --- MAIN LOGIC ---
if submitted:
    if not wallet_address:
        st.warning("Vui lòng nhập địa chỉ ví.")
    elif not date_range or len(date_range) != 2:
        st.warning("Vui lòng chọn khoảng thời gian hợp lệ.")
    else:
        start_d, end_d = date_range
        with st.spinner(f"Đang truy vết ví {wallet_address}..."):
            data = client.fetch_trace_data(wallet_address, str(start_d), str(end_d))
            st.session_state['wallet_data'] = data # Lưu vào state
            st.session_state['ai_analysis'] = None

# --- DISPLAY RESULTS ---
if 'wallet_data' in st.session_state and st.session_state['wallet_data']:
    data = st.session_state['wallet_data']
    st.header(f"Kết quả cho ví: `{data['address']}`")
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Tổng Giao Dịch", f"{data['total_transactions']:,}")
    col2.metric("Tổng Nhận (sats)", f"{data['total_received']:,}")
    col3.metric("Số Dư Cuối (sats)", f"{data['final_balance']:,}")

    # Associated Addresses
    if data['associated_addresses']:
        with st.expander("🔗 Các địa chỉ liên quan (có thể cùng chủ sở hữu)"):
            st.json(data['associated_addresses'])
    
    # Charts and Data
    transactions = data.get('transactions', [])
    if transactions:
        df_tx = pd.DataFrame(transactions)
        df_tx['time'] = pd.to_datetime(df_tx['status'].apply(lambda x: x['block_time']), unit='s')
        
        charts.create_frequency_chart(df_tx)
        
        st.subheader("📑 Chi tiết giao dịch")
        for i, tx in enumerate(transactions):
            with st.expander(f"TXID: {tx['txid']} - Nhãn: **{tx['analysis_label']}**"):
                col_a, col_b = st.columns([1,2])
                with col_a:
                    st.write(f"**Thời gian:** {df_tx.loc[i, 'time']}")
                    st.write(f"**Phí:** {tx['fee']:,} sats")
                    st.write(f"**Inputs:** {len(tx['vin'])}")
                    st.write(f"**Outputs:** {len(tx['vout'])}")
                with col_b:
                    charts.create_sankey_chart_for_tx(tx)
    else:
        st.info("Không có giao dịch nào trong khoảng thời gian đã chọn.")

    # AI Analysis Section
    st.divider()
    st.header("🤖 Phân Tích Chuyên Sâu Bằng AI")
    openai_key = st.text_input("Nhập OpenAI API Key", type="password")
    if st.button("🧠 Phân tích ngay!", disabled=not openai_key):
        with st.spinner("AI đang phân tích, vui lòng đợi..."):
            ai_result = client.fetch_ai_analysis(data, openai_key)
            st.session_state['ai_analysis'] = ai_result

    if 'ai_analysis' in st.session_state and st.session_state['ai_analysis']:
        st.markdown(st.session_state['ai_analysis'])

