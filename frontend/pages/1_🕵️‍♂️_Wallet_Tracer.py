import streamlit as st
import time
import datetime
import threading
import pandas as pd
from frontend.api import client
from frontend.components import charts

st.set_page_config(page_title="Wallet Tracer", layout="wide", page_icon="📊")

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Vui lòng đăng nhập để truy cập trang này.")
    st.page_link("Home.py", label="Về trang Đăng nhập", icon="🏠")
    st.stop()

def trigger_tracer_ai_analysis(results_data):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: trigger_tracer_ai_analysis                          ##
    ##                                                                ##
    ##  - Purpose: This function is designed to run in a separate     ##
    ##    background thread. Its sole job is to trigger the AI report ##
    ##    generation process without freezing the user interface.     ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - results_data (dict): The complete analysis object that    ##
    ##      was previously fetched and stored in `st.session_state`.  ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Sets a session state flag (`tracer_ai_is_running`) to    ##
    ##       `True` to let the main UI know that an analysis is in    ##
    ##       progress.                                                ##
    ##    2. Clears any previous AI report content.                   ##
    ##    3. Calls the `client.generate_ai_report` function, which    ##
    ##       sends the analysis data to the backend API.              ##
    ##    4. Upon receiving a response, it updates the session state  ##
    ##       (`ai_report_content`) with the new report text or an     ##
    ##       error message.                                           ##
    ##    5. Finally, it sets the `tracer_ai_is_running` flag back to ##
    ##       `False`.                                                 ##
    ##                                                                ##
    ##  - Output: This function does not return a value directly.     ##
    ##    Instead, it modifies `st.session_state` to communicate its  ##
    ##    results and status back to the main Streamlit thread.       ##
    ##                                                                ##
    ####################################################################
    st.session_state.tracer_ai_is_running = True
    st.session_state.ai_report_content = "" 
    try:
        ai_response = client.generate_ai_report(results_data)
        st.session_state.ai_report_content = ai_response.get('report_text')
    except Exception as e:
        st.session_state.ai_report_content = f"**Đã xảy ra lỗi khi tạo báo cáo:**\n\n{e}"
    finally:
        st.session_state.tracer_ai_is_running = False

with st.sidebar:
    st.header("⚙️ Bảng Điều Khiển")

    address_input = st.text_input(
        "Nhập địa chỉ ví Bitcoin:", 
        placeholder="Ví dụ: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
    )
    
    today = datetime.date.today()
    ninety_days_ago = today - datetime.timedelta(days=90)
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Từ ngày", ninety_days_ago)
    end_date = col2.date_input("Đến ngày", today)
    
    analyze_button = st.button("🚀 Phân Tích Ví", use_container_width=True, type="primary")
    
    st.markdown("---")
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.success("Đăng nhập thành công!")
        st.write(f"Tài khoản: demo@dotoshi.com")
        if st.button("Đăng xuất"):
            del st.session_state.logged_in
            st.rerun()

st.title("📊 Wallet Tracer - Phân Tích Ví Bitcoin Chuyên Sâu")
st.markdown("---")

if analyze_button:
    if not address_input:
        st.error("Vui lòng nhập địa chỉ ví Bitcoin.")
    elif start_date > end_date:
        st.error("Ngày bắt đầu không được lớn hơn ngày kết thúc.")
    else:
        st.session_state.wallet_address = address_input
        with st.spinner("Đang lấy và phân tích dữ liệu..."):
            try:
                results = client.get_analysis_results(address=address_input, start_date=str(start_date), end_date=str(end_date))
                st.session_state.analysis_results = results
                st.session_state.ai_report_content = None            
                st.session_state.error = None
            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.analysis_results = None

if 'error' in st.session_state and st.session_state.error:
    st.error(f"Đã có lỗi xảy ra: {st.session_state.error}")

if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    results = st.session_state.analysis_results

    with st.container(border=True):
        st.subheader("📈 Kết Luận Phân Tích Nhanh")
        col1, col2, col3 = st.columns([3, 1.5, 1.5])
        
        wallet_profile = results['wallet_profile_classified']
        profile_icon = wallet_profile.split(" ")[0]
        profile_text = " ".join(wallet_profile.split(" ")[1:])
        col1.metric(f"🏷️ Phân Loại Ví", value=profile_text)
        
        risk_profile = results['risk_analysis']['profile']
        risk_icon = "🔴" if "Cao" in risk_profile else ("🟠" if "Trung bình" in risk_profile else "🟢")
        col2.metric(f"{risk_icon} Hồ Sơ Rủi Ro", value=risk_profile)
        
        risk_score = results['risk_analysis']['risk_score']
        score_icon = "🚨" if risk_score > 70 else "✅"
        col3.metric(f"{score_icon} Điểm Rủi Ro", value=f"{risk_score}/100")

    with st.container(border=True):
        st.subheader("💰 Thống Kê Chung (Toàn Lịch Sử)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tổng Giao Dịch", f"{results['chain_stats']['tx_count']:,}")
        c2.metric("Đã Nhận (BTC)", f"{(results['chain_stats']['funded_txo_sum'] / 1e8):.4f}")
        c3.metric("Đã Gửi (BTC)", f"{(results['chain_stats']['spent_txo_sum'] / 1e8):.4f}")
        c4.metric("Số Dư Hiện Tại (BTC)", f"{(results['chain_stats']['funded_txo_sum'] - results['chain_stats']['spent_txo_sum']) / 1e8:.4f}")

    tab_charts, tab_red_flags, tab_transactions = st.tabs(["📊 Biểu Đồ", "🚩 Cờ Đỏ & Rủi Ro", "📋 Giao Dịch Chi Tiết"])

    with tab_charts:
        with st.container(border=True):
            chart_type_volume = st.radio("Khối lượng:", ['Cột', 'Đường'], horizontal=True, index=0)
            charts.render_volume_chart(results['wallet_data']['transactions'], chart_type_volume)
        st.markdown("---")
        with st.container(border=True):
            chart_type_frequency = st.radio("Tần suất:", ['Cột', 'Đường'], horizontal=True, index=0)
            charts.render_frequency_chart(results['wallet_data']['transactions'], chart_type_frequency)
            
        st.markdown("---")
        st.subheader("🤖 Phân Tích Chuyên Sâu bằng AI")
        st.info("Nhấn nút bên dưới để gửi dữ liệu của ví này cho GPT-4 và nhận lại một bản báo cáo tình báo chuyên sâu.")

        col1, col2 = st.columns([1, 4]) 

        with col1:
            if st.button(
                "🚀 Chạy Phân tích AI",
                help="Tạo Báo cáo Phân tích bằng AI",
                type="primary",
                use_container_width=True 
            ):
                with st.spinner("AI đang phân tích... Quá trình này có thể mất 1-2 phút, vui lòng không rời khỏi trang."):
                    try:
                        ai_response = client.generate_ai_report(
                            address=address_input,
                            start_date=str(start_date),
                            end_date=str(end_date)
                        )
    
                        st.session_state.ai_report_content_tracer = ai_response.get('report_text', "Lỗi: Không nhận được nội dung từ AI.")

                    except Exception as e:
                        st.session_state.ai_report_content_tracer = f"**Đã xảy ra lỗi khi tạo báo cáo:**\n\n{e}"
                
                
        if 'ai_report_content_tracer' in st.session_state and st.session_state.ai_report_content_tracer:
            st.markdown("---")
            st.subheader("📝 Báo cáo Phân tích của AI")
            with st.container(border=True):
                st.markdown(st.session_state.ai_report_content_tracer)

    with tab_red_flags:
        red_flags = results['risk_analysis'].get('red_flags', {})
        flag_titles = {"high_value_transactions": "Giao dịch giá trị cao", "peel_chains": "Chuỗi lột vỏ (Peel Chains)", "structuring_transactions": "Giao dịch cấu trúc (Structuring)", "complex_mimo_transactions": "Giao dịch phức tạp (Nhiều vào/Nhiều ra)", "address_reuse": "Tái sử dụng địa chỉ"}
        
        found_any_flag = any(
            (isinstance(val, list) and val) or 
            (isinstance(val, dict) and val.get('verdict') == 'Thường xuyên') 
            for val in red_flags.values()
        )
        
        if not found_any_flag:
            st.success("✅ Không tìm thấy dấu hiệu rủi ro nào đáng kể trong khoảng thời gian phân tích.")
        else:
            for key, value in red_flags.items():
                if (isinstance(value, list) and value) or (isinstance(value, dict) and value.get('verdict') == 'Thường xuyên'):
                    with st.expander(f"🚩 **{flag_titles.get(key, key)}** - ({len(value) if isinstance(value, list) else value.get('count', 0)} lần)", expanded=True):
                        if key == 'address_reuse':
                            st.info(value.get('reason'))
                        else:
                            for item in value:
                                txid_link = f"https://mempool.space/tx/{item.get('txid')}"
                                st.markdown(f"- **TXID**: <a href='{txid_link}' target='_blank'>{item.get('txid')}</a> - *Lý do*: {item.get('reason')}", unsafe_allow_html=True)


    with tab_transactions:

        label_badge_color_map = {
            "Peel Chain": "#FF7F50",      
            "Gom Coin": "#1E90FF",        
            "Phân Tán": "#169E26",        
            "Phức Tạp": "#DC143C",        
            "Tiêu Chuẩn": "#8828D7"       
        }

        label_text_color_map = {
            "Peel Chain": "orange",
            "Gom Coin": "blue",
            "Phân Tán": "green",
            "Phức Tạp": "red",
            "Tiêu Chuẩn": "violet"         
        }

        sorted_txs = sorted(results['wallet_data']['transactions'], key=lambda x: x.get('block_time_iso', '1970-01-01T00:00:00'), reverse=True)
        
        st.write(f"Tìm thấy {len(sorted_txs)} giao dịch trong khoảng thời gian đã chọn.")
        for tx in sorted_txs:
            tx_time = pd.to_datetime(tx['block_time_iso']).strftime('%d-%m-%Y %H:%M:%S')
            delta_sats = tx.get('balance_delta', 0)
            delta_btc = delta_sats / 1e8
            delta_display = f"🟢 +{delta_btc:,.8f} BTC" if delta_sats > 0 else (f"🔴 {delta_btc:,.8f} BTC" if delta_sats < 0 else "⚪️ Tương tác")
            
            tx_label = tx.get('transaction_label', 'Tiêu Chuẩn')
            
            text_color = label_text_color_map.get(tx_label, "gray")
            styled_label = f":{text_color}[{tx_label}]"

            expander_title = f"{tx_time} | {styled_label} | {delta_display}"
            
            with st.expander(expander_title):

                badge_color = label_badge_color_map.get(tx_label, "#808080")
                st.markdown(f"**Loại giao dịch:** <span style='background-color:{badge_color}; color:white; padding: 3px 10px; border-radius: 15px; font-size: 0.9em;'>{tx_label}</span>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.write(f"**TXID**: [{tx['txid'][:12]}...](https://mempool.space/tx/{tx['txid']})")
                    st.write(f"**Đầu vào:** {len(tx['vin'])} | **Đầu ra:** {len(tx['vout'])}")
                    st.write(f"**Phí:** {tx['fee']:,} sats")
                with col2:
                    charts.render_sankey_for_transaction(tx, main_address=address_input)
                    
    
