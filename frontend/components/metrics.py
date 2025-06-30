import streamlit as st
import pandas as pd
from . import charts 

def display_overview(results: dict):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: display_overview                                    ##
    ##                                                                ##
    ##  - Purpose: To render the main summary cards at the top of the ##
    ##    "Wallet Tracer" page. It provides a high-level, at-a-glance ##
    ##    summary of the analysis.                                    ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - results (dict): The complete analysis object returned     ##
    ##      from the backend.                                         ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Extracts key data points: `risk_analysis`,               ##
    ##       `wallet_profile_classified`, and `chain_stats`.          ##
    ##    2. Uses `st.columns` to create a clean layout for the cards.##
    ##    3. Uses `st.metric` to display each key statistic, such as  ##
    ##       Wallet Profile, Risk Profile, and overall stats like     ##
    ##       Total Received/Sent.                                     ##
    ##                                                                ##
    ##  - Output: Renders several formatted metric cards directly     ##
    ##    into the Streamlit app.                                     ##
    ##                                                                ##
    ####################################################################
    st.subheader("Kết Luận Phân Tích Nhanh")
    risk_analysis = results.get('risk_analysis', {})
    wallet_profile = results.get('wallet_profile_classified', 'N/A')
    chain_stats = results.get('chain_stats', {})
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Phân Loại Ví", value=wallet_profile)
    col2.metric("Hồ Sơ Rủi Ro", value=risk_analysis.get('profile', 'N/A'))
    col3.metric("Điểm Rủi Ro", f"{risk_analysis.get('risk_score', 0)}/100", help="Điểm càng cao, rủi ro càng lớn.")
    
    st.markdown("---")
    st.subheader("Thống Kê Chung (Toàn Lịch Sử)")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng Giao Dịch", f"{chain_stats.get('tx_count', 0):,}")
    c2.metric("Đã Nhận (BTC)", f"{(chain_stats.get('funded_txo_sum', 0) / 1e8):.4f}")
    c3.metric("Đã Gửi (BTC)", f"{(chain_stats.get('spent_txo_sum', 0) / 1e8):.4f}")
    c4.metric("Số Dư Hiện Tại (BTC)", f"{((chain_stats.get('funded_txo_sum', 0) - chain_stats.get('spent_txo_sum', 0)) / 1e8):.4f}")

def display_red_flags(risk_analysis: dict):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: display_red_flags                                   ##
    ##                                                                ##
    ##  - Purpose: To display a detailed breakdown of all the "Red    ##
    ##    Flags" that were identified during the backend analysis.    ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - risk_analysis (dict): The specific part of the analysis   ##
    ##      results that contains the `red_flags` data.               ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Iterates through each type of red flag (e.g.,            ##
    ##       "high_value_transactions", "peel_chains").               ##
    ##    2. If a flag category contains any items, it creates an     ##
    ##       expandable section (`st.expander`) for it.               ##
    ##    3. Inside the expander, it lists each flagged transaction,  ##
    ##       providing the reason and a clickable link to a block     ##
    ##       explorer for further investigation.                      ##
    ##                                                                ##
    ##  - Output: Renders a user-friendly, expandable list of all     ##
    ##    potential risks on the Streamlit UI. If no flags are found, ##
    ##    it displays a success message.                              ##
    ##                                                                ##
    ####################################################################
    st.subheader("Phân Tích Dấu Hiệu Rủi Ro")
    red_flags = risk_analysis.get('red_flags', {})
    flag_titles = {
        "high_value_transactions": "Giao dịch giá trị cao",
        "peel_chains": "Chuỗi lột vỏ (Peel Chains)",
        "structuring_transactions": "Giao dịch cấu trúc (Structuring)",
        "complex_mimo_transactions": "Giao dịch phức tạp (Nhiều vào/Nhiều ra)",
        "address_reuse": "Tái sử dụng địa chỉ"
    }
    found_any_flag = False
    for key, value in red_flags.items():
        if (isinstance(value, list) and value) or (isinstance(value, dict) and value.get('verdict') == 'Thường xuyên'):
            found_any_flag = True
            with st.expander(f"🚩 {flag_titles.get(key, key)} ({len(value) if isinstance(value, list) else value.get('count', 0)} lần)", expanded=True):
                if key == 'address_reuse':
                    st.write(value.get('reason'))
                else:
                    for item in value:
                        st.markdown(f"- **TXID**: `https://mempool.space/tx/{item.get('txid')}` - *Lý do*: {item.get('reason')}")
    if not found_any_flag:
        st.success("✅ Không tìm thấy dấu hiệu rủi ro nào đáng kể.")

def display_transaction_details(transactions: list):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: display_transaction_details                         ##
    ##                                                                ##
    ##  - Purpose: To render a detailed, interactive list of all      ##
    ##    transactions within the selected date range.                ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (list): A list of transaction dictionaries.  ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Sorts the transactions by block time to show the most    ##
    ##       recent ones first.                                       ##
    ##    2. Iterates through each transaction, creating an           ##
    ##       expandable section (`st.expander`) for it.               ##
    ##    3. The expander's title provides a quick summary: timestamp,##
    ##       transaction label, and value change.                     ##
    ##    4. Inside the expander, it displays detailed information    ##
    ##       (TXID, fee, etc.) and calls the                          ##
    ##       `charts.render_sankey_for_transaction` function to       ##
    ##       visualize the fund flow for that specific transaction.   ##
    ##                                                                ##
    ##  - Output: Renders a comprehensive and interactive list of     ##
    ##    transactions in the Streamlit app.                          ##
    ##                                                                ##
    ####################################################################
    st.subheader(f"Tìm thấy {len(transactions)} giao dịch")
    if not transactions:
        st.warning("Không có giao dịch nào trong khoảng thời gian đã chọn.")
        return

    sorted_transactions = sorted(transactions, key=lambda x: x['status']['block_time'], reverse=True)

    for tx in sorted_transactions:
        tx_time = pd.to_datetime(tx['status']['block_time'], unit='s').strftime('%Y-%m-%d %H:%M:%S')
        delta_sats = tx['balance_delta']
        delta_btc = delta_sats / 1e8
        
        if delta_sats > 0:
            delta_display = f"🟢 +{delta_btc:,.8f} BTC"
        elif delta_sats < 0:
            delta_display = f"🔴 {delta_btc:,.8f} BTC"
        else:
            delta_display = f"⚪ 0 BTC"

        with st.expander(f"{tx_time} | **{tx['transaction_label']}** | {delta_display}"):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.write("**Thông tin giao dịch**")
                st.markdown(f"**TXID**: [{tx['txid'][:15]}...](https://mempool.space/tx/{tx['txid']})")
                st.write(f"**Số đầu vào**: {len(tx['vin'])}")
                st.write(f"**Số đầu ra**: {len(tx['vout'])}")
                st.write(f"**Phí**: {tx['fee']:,} sats")
                st.write(f"**Tổng giá trị**: {tx['total_value']:,} sats")
            
            with col2:
                charts.render_sankey_for_transaction(tx)
