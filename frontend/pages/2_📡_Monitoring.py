import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import time
import websocket
import threading
import json
import queue
import datetime
from collections import deque
from frontend.api import client

if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("🔒 Vui lòng đăng nhập để truy cập trang này.")
    st.page_link("Home.py", label="Về trang Đăng nhập", icon="🏠")
    st.stop()

st.set_page_config(page_title="Dashboard Giám Sát", layout="wide", page_icon="📡")

st.markdown("""
<style>
    div[data-testid="stHorizontalBlock"] > div[data-testid="stVerticalBlock"] {
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: init_session_state                                  ##
    ##                                                                ##
    ##  - Purpose: To safely initialize all necessary keys in         ##
    ##    Streamlit's session_state at the beginning of the script.   ##
    ##    This prevents AttributeError exceptions when a key is       ##
    ##    accessed before it's assigned, ensuring that variables like ##
    ##    lists, queues, and dictionaries exist from the very first   ##
    ##    run.                                                        ##
    ##                                                                ##
    ##  - Input: None. It operates directly on st.session_state.      ##
    ##                                                                ##
    ##  - Process: It iterates through a predefined dictionary of     ##
    ##    keys and their default values. For each key, it checks if   ##
    ##    it already exists in st.session_state. If not, it creates   ##
    ##    the key and assigns the default value.                      ##
    ##                                                                ##
    ##  - Output: None. It modifies st.session_state in place.        ##
    ##                                                                ##
    ####################################################################
    keys = {
        'monitored_addresses': [], 'wallet_profiles': {}, 'alerts': deque(maxlen=50),
        'alert_queue': queue.Queue(), 'mempool_tx_queue': queue.Queue(),
        'recent_mempool_txs': deque(maxlen=20), 'selected_address': 'Tất cả',
        'ai_results': {}, 
        'ai_last_run': {}, 
        'ai_is_running': {}
    }
    for key, default_value in keys.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

@st.cache_data(ttl=900)
def get_chart_data(chart_name):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: get_chart_data                                      ##
    ##                                                                ##
    ##  - Purpose: To fetch historical chart data (e.g., transaction  ##
    ##    counts, confirmation times) from the blockchain.info API.   ##
    ##    It is decorated with @st.cache_data to avoid re-fetching    ##
    ##    the same data frequently, significantly improving           ##
    ##    performance and reducing API calls.                         ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - chart_name (str): The specific name of the chart to fetch ##
    ##      (e.g., "n-transactions-total", "median-confirmation-time")##
    ##                                                                ##
    ##  - Output: A pandas DataFrame containing the historical data   ##
    ##    for the requested chart, indexed by date. Returns an empty  ##
    ##    DataFrame on failure.                                       ##
    ##                                                                ##
    ####################################################################
    try:
        url = f"https://api.blockchain.info/charts/{chart_name}?timespan=1year&rollingAverage=7days&format=json"
        response = requests.get(url); response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['values']); df['x'] = pd.to_datetime(df['x'], unit='s')
        return df.set_index('x')
    except Exception: return pd.DataFrame()

@st.cache_data(ttl=3600)
def create_wallet_profile(address):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: create_wallet_profile                               ##
    ##                                                                ##
    ##  - Purpose: To create a basic behavioral profile for a given   ##
    ##    Bitcoin address. It fetches recent transactions to calculate##
    ##    baseline metrics like average transaction value and standard##
    ##    deviation, which are crucial for the anomaly detection      ##
    ##    function.                                                   ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The Bitcoin address to profile.            ##
    ##                                                                ##
    ##  - Output: A dictionary containing the calculated metrics:     ##
    ##    {"avg_value_btc": ..., "std_dev_btc": ...}.                 ##
    ##                                                                ##
    ####################################################################
    try:
        response = requests.get(f"https://mempool.space/api/address/{address}/txs")
        txs = response.json()
        if not txs: return {"avg_value_btc": 0, "std_dev_btc": 0}
        values = [sum(o.get('value', 0) for o in tx.get('vout', [])) / 1e8 for tx in txs]
        return {"avg_value_btc": np.mean(values) if values else 0, "std_dev_btc": np.std(values) if values else 0}
    except Exception: return {"avg_value_btc": 0, "std_dev_btc": 0}

def score_transaction_risk(tx, wallet_profile):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: score_transaction_risk                              ##
    ##                                                                ##
    ##  - Purpose: To analyze a single transaction and assign a risk  ##
    ##    score based on a set of predefined heuristics. This         ##
    ##    simulates a simple machine learning model for anomaly       ##
    ##    detection by flagging suspicious patterns.                  ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - tx (dict): The transaction data object.                   ##
    ##    - wallet_profile (dict): The pre-calculated profile for the ##
    ##      involved wallet, containing its historical metrics.       ##
    ##                                                                ##
    ##  - Output: A tuple containing an integer risk score (0-100)    ##
    ##    and a list of strings describing the reasons for the score. ##
    ##                                                                ##
    ####################################################################
    score, reasons = 0, []
    total_value_btc = sum(out.get('value', 0) for out in tx.get('out', [])) / 1e8
    avg_val, std_dev = wallet_profile.get('avg_value_btc', 0), wallet_profile.get('std_dev_btc', 1)
    threshold = (avg_val + 3 * std_dev) if avg_val > 0 and std_dev > 0 else 10
    if total_value_btc > threshold and total_value_btc > 0.1:
        score += 40; reasons.append(f"Giá trị lớn bất thường ({total_value_btc:.2f} BTC)")
    inputs, outputs = tx.get('inputs', []), tx.get('out', [])
    if len(inputs) == 1 and len(outputs) > 2: score += 10; reasons.append("Có dấu hiệu Peeling Chain")
    if len(inputs) > 5 and len(outputs) == 1: score += 25; reasons.append("Có dấu hiệu Gom Coin")
    return min(score, 100), reasons

def websocket_listener(addresses, alert_q, mempool_q, profiles):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: websocket_listener                                  ##
    ##                                                                ##
    ##  - Purpose: To run continuously in a background thread,        ##
    ##    listening for real-time data from the blockchain.com        ##
    ##    WebSocket API. This is the core of the real-time monitoring ##
    ##    feature.                                                    ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - addresses (list): A list of wallet addresses to monitor.  ##
    ##    - alert_q (queue.Queue): A thread-safe queue to pass alerts.##
    ##    - mempool_q (queue.Queue): A thread-safe queue for all txs. ##
    ##    - profiles (dict): The dictionary of wallet profiles.       ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Establishes a persistent WebSocket connection.           ##
    ##    2. Subscribes to all unconfirmed transactions and to        ##
    ##       transactions specific to the monitored addresses.        ##
    ##    3. On receiving a new transaction, it's put into the        ##
    ##       `mempool_q`. If it involves a monitored address, it is   ##
    ##       scored for risk, and an alert is put into `alert_q` if   ##
    ##       it's anomalous.                                          ##
    ##                                                                ##
    ##  - Output: None. It communicates with the main thread via the  ##
    ##    provided queues.                                            ##
    ##                                                                ##
    ####################################################################
    ws_url = "wss://ws.blockchain.info/inv"
    def on_message(ws, message):
        data = json.loads(message)
        if data.get('op') == 'utx':
            tx = data.get('x', {})
            mempool_q.put(tx)
            involved_addrs = {out.get('addr') for out in tx.get('out', []) if out.get('addr')} | {inp.get('prev_out', {}).get('addr') for inp in tx.get('inputs', []) if inp.get('prev_out')}
            for addr in addresses:
                if addr in involved_addrs:
                    risk_score, reasons = score_transaction_risk(tx, profiles.get(addr, {}))
                    if risk_score > 40:
                        alert_q.put({"tx": tx, "score": risk_score, "reasons": reasons, "address": addr, "timestamp": datetime.datetime.now()})
                        break
    def on_open(ws):
        ws.send(json.dumps({"op": "unconfirmed_sub"}))
        for addr in addresses:
            ws.send(json.dumps({"op": "addr_sub", "addr": addr}))
    ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message)
    ws.run_forever()

def trigger_ai_analysis(address):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: trigger_ai_analysis                                 ##
    ##                                                                ##
    ##  - Purpose: To be the target function for a background thread  ##
    ##    that handles the AI analysis polling. It calls the backend  ##
    ##    API to get an AI analysis for a specific wallet without     ##
    ##    freezing the UI.                                            ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The wallet address to be analyzed.         ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Sets a flag in `session_state` (`ai_is_running`) to True ##
    ##    2. Calls the `client.get_polling_ai_analysis` function.     ##
    ##    3. When the result is received, it updates `session_state`  ##
    ##       with the AI's text or an error message.                  ##
    ##    4. Sets the `ai_is_running` flag to `False` and records the ##
    ##       timestamp of the run.                                    ##
    ##                                                                ##
    ##  - Output: None. It modifies `st.session_state` to communicate ##
    ##    its status and results.                                     ##
    ##                                                                ##
    ####################################################################
    st.session_state.ai_is_running[address] = True
    st.session_state.ai_results[address] = "" 
    try:
        result = client.get_ai_analysis(address)
        st.session_state.ai_results[address] = result.get("analysis_text", "Không có nội dung phân tích.")
    except Exception as e:
        st.session_state.ai_results[address] = f"**Đã xảy ra lỗi:**\n\n{str(e)}"
    finally:
        st.session_state.ai_is_running[address] = False
        st.session_state.ai_last_run[address] = datetime.datetime.now()

st.title("📡 Dashboard Giám Sát Chuyên Sâu")

main_cols = st.columns([1.5, 2], gap="large")

with main_cols[0]:
    st.subheader("⚙️ Quản Lý Ví")
    with st.container(border=True):
        new_address = st.text_input("Thêm địa chỉ ví mới:", placeholder="Nhập địa chỉ và bấm 'Thêm'")
        if st.button("➕ Thêm Ví", use_container_width=True, type="primary"):
            if new_address and new_address not in st.session_state.monitored_addresses:
                with st.spinner("Đang tạo hồ sơ cho ví..."):
                    profile = create_wallet_profile(new_address)
                    st.session_state.wallet_profiles[new_address] = profile
                st.session_state.monitored_addresses.append(new_address)
                
                st.toast(f"Đang gửi yêu cầu phân tích AI lần đầu cho ví mới...", icon="🤖")
                threading.Thread(target=trigger_ai_analysis, args=(new_address,), daemon=True).start()
        
                st.rerun()

        if st.session_state.monitored_addresses:
            st.markdown("**Danh sách đang giám sát:**")
            for i in range(len(st.session_state.monitored_addresses) - 1, -1, -1):
                addr = st.session_state.monitored_addresses[i]
                c1, c2 = st.columns([10, 1])
                c1.code(addr, language=None)
                if c2.button("🗑️", key=f"del_{addr}", help="Xóa ví này"):
                    del st.session_state.wallet_profiles[addr]
                    st.session_state.monitored_addresses.pop(i)
                    st.rerun()

    selected_address = st.selectbox(
        "Chọn ví:", 
        options=["Tất cả"] + st.session_state.monitored_addresses,
        key='selected_address'
    )
    
    st.subheader("🚨 Cảnh Báo Real-time")
    alerts_placeholder = st.empty()

with main_cols[1]:
    st.subheader("🌊 Luồng Giao Dịch Blockchain (Real-time)")
    mempool_placeholder = st.empty()

st.markdown("---")
st.subheader("📈 Tổng Quan Mạng Lưới Bitcoin")

row1_cols = st.columns(2, gap="large")
row2_cols = st.columns(2, gap="large")
charts_map = {
    "n-transactions-total": (row1_cols[0], "Tổng số giao dịch", px.colors.sequential.Teal),
    "n-transactions": (row1_cols[1], "Số giao dịch mỗi ngày", px.colors.sequential.Aggrnyl),
    "median-confirmation-time": (row2_cols[0], "Thời gian xác nhận TB (phút)", px.colors.sequential.OrRd),
    "n-transactions-per-block": (row2_cols[1], "Giao dịch TB mỗi khối", px.colors.sequential.Purp)
}

for chart_name, (col, title, color_scale) in charts_map.items():
    with col:
        with st.container(border=True):
            df = get_chart_data(chart_name)
            st.markdown(f"**{title}**")
            if not df.empty:
                fig = go.Figure([go.Scatter(x=df.index, y=df['y'], fill='tozeroy', mode='lines', line_color=color_scale[-2])])
                fig.update_layout(height=280, template="plotly_white", showlegend=False, margin=dict(l=5, r=5, t=10, b=5), yaxis_title="", xaxis_title="")
                st.plotly_chart(fig, use_container_width=True)

if st.session_state.monitored_addresses and ('monitor_thread' not in st.session_state or not st.session_state.monitor_thread.is_alive()):
    st.toast("Kích hoạt luồng giám sát...", icon="✅")
    thread = threading.Thread(
        target=websocket_listener, 
        args=(
            st.session_state.monitored_addresses, 
            st.session_state.alert_queue, 
            st.session_state.mempool_tx_queue, 
            st.session_state.wallet_profiles
        ), 
        daemon=True
    )
    st.session_state.monitor_thread = thread
    thread.start()

st.markdown("---")
st.subheader("🤖 Phân Tích bằng AI (Tự động cập nhật 5 phút/lần)")
ai_placeholder = st.empty()

@st.fragment
def update_ui_loop():
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: update_ui_loop                                      ##
    ##                                                                ##
    ##  - Purpose: This is the main UI rendering loop, decorated with ##
    ##    `@st.fragment`. It runs continuously to create a real-time  ##
    ##    feel, updating the dashboard sections without a full page   ##
    ##    reload.                                                     ##
    ##                                                                ##
    ##  - Input: None. It reads directly from `st.session_state`.     ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Enters an infinite `while True` loop.                    ##
    ##    2. Drains the `alert_queue` and `mempool_tx_queue`.         ##
    ##    3. Re-draws the content inside the `alerts_placeholder` and ##
    ##       `mempool_placeholder` based on the latest data.          ##
    ##    4. Implements the AI Polling logic by checking the time     ##
    ##       since the last analysis for the selected wallet.         ##
    ##    5. Pauses for 2 seconds before the fragment re-runs.        ##
    ##                                                                ##
    ##  - Output: Renders the dynamic parts of the UI.                ##
    ##                                                                ##
    ####################################################################
    while True:
        selected_address = st.session_state.get('selected_address', 'Tất cả')

        while not st.session_state.alert_queue.empty():
            st.session_state.alerts.appendleft(st.session_state.alert_queue.get())
        while not st.session_state.mempool_tx_queue.empty():
            st.session_state.recent_mempool_txs.appendleft(st.session_state.mempool_tx_queue.get())

        with alerts_placeholder.container(height=500):
            alerts_to_show = [a for a in st.session_state.alerts if selected_address == "Tất cả" or a['address'] == selected_address]
            if not alerts_to_show: st.info("Chưa có cảnh báo cho lựa chọn này...")
            else:
                for alert in alerts_to_show:
                    with st.container(border=True):
                        st.error(f"**Lý do:** {alert['reasons'][0]} (Điểm: {alert['score']})")
                        st.markdown(f"**Ví:** `{alert['address']}` | **TXID:** [{alert['tx']['hash'][:15]}...](https://mempool.space/tx/{alert['tx']['hash']})")
                        st.caption(f"Thời gian: {alert['timestamp'].strftime('%H:%M:%S')}")

        with mempool_placeholder.container(height=560):
            mempool_to_show = st.session_state.recent_mempool_txs if selected_address == "Tất cả" else [tx for tx in st.session_state.recent_mempool_txs if selected_address in ({o.get('addr') for o in tx.get('out',[])} | {i.get('prev_out',{}).get('addr') for i in tx.get('inputs',[])})]
            st.caption(f"Hiển thị giao dịch cho: {selected_address}")
            if not mempool_to_show: st.info("Đang chờ giao dịch...")
            else:
                for tx in mempool_to_show:
                    tx_hash, total_value = tx.get('hash', 'N/A'), sum(out.get('value', 0) for out in tx.get('out', [])) / 1e8
                    tx_time, num_inputs, num_outputs = datetime.datetime.fromtimestamp(tx.get('time')).strftime('%H:%M:%S'), len(tx.get('inputs', [])), len(tx.get('out', []))
                    st.markdown(f"**TX:** [{tx_hash[:12]}...](https://mempool.space/tx/{tx_hash}) | **Time:** `{tx_time}` | **Value:** `{total_value:.4f} BTC` | **In/Out:** `{num_inputs}/{num_outputs}`")
        
        with ai_placeholder.container(border=True):
            if selected_address == "Tất cả":
                st.info("Hãy chọn một ví cụ thể để xem hoặc chạy phân tích AI.")
            else:
                is_running = st.session_state.ai_is_running.get(selected_address, False)
                last_run = st.session_state.ai_last_run.get(selected_address)
                
                if is_running:
                    with st.spinner(f"AI đang phân tích ví {selected_address[:10]}..."):
                        for _ in range(15): time.sleep(1) 
                else:
                    should_rerun_ai = not last_run or (datetime.datetime.now() - last_run).total_seconds() > 300
                    if should_rerun_ai:
                        st.info(f"Đang gửi yêu cầu phân tích mới cho ví {selected_address[:10]}...")
                        threading.Thread(target=trigger_ai_analysis, args=(selected_address,), daemon=True).start()
                    
                    analysis_content = st.session_state.ai_results.get(selected_address)
                    if analysis_content:
                        st.markdown(analysis_content)
                        if last_run: st.caption(f"Phân tích gần nhất lúc: {last_run.strftime('%H:%M:%S')}.")
                    else:
                        st.info("Chưa có phân tích cho ví này. Quá trình sẽ tự động bắt đầu.")

        time.sleep(2)

if st.session_state.monitored_addresses:
    update_ui_loop()
else:
    alerts_placeholder.info("Thêm một địa chỉ ví để bắt đầu giám sát.")
    
