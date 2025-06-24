import requests
import streamlit as st
import os

# --- Phiên bản cuối cùng, hoạt động linh hoạt trên cả local và server ---

# Đọc URL của backend từ biến môi trường.
# Nếu không có (khi chạy ở local), nó sẽ sử dụng giá trị mặc định.
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

def fetch_trace_data(address: str, start_date: str, end_date: str):
    """Gọi API để lấy dữ liệu truy vết."""
    url = f"{BACKEND_URL}/tracing/trace/{address}"
    params = {"start_date": start_date, "end_date": end_date}
    try:
        response = requests.get(url, params=params, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Cố gắng phân tích JSON từ lỗi, nếu không được thì hiển thị text thô
        try:
            detail = e.response.json().get('detail', e.response.text)
        except requests.exceptions.JSONDecodeError:
            detail = e.response.text
        st.error(f"Lỗi truy vết (HTTP {e.response.status_code}): {detail}")
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối đến backend: {e}")
    return None

def fetch_ai_analysis(wallet_data: dict, api_key: str):
    """Gọi API để lấy phân tích AI."""
    url = f"{BACKEND_URL}/tracing/analyze-ai"
    payload = {
        "wallet_data": wallet_data,
        "openai_api_key": api_key
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json().get("analysis")
    except requests.exceptions.HTTPError as e:
        try:
            detail = e.response.json().get('detail', e.response.text)
        except requests.exceptions.JSONDecodeError:
            detail = e.response.text
        st.error(f"Lỗi phân tích AI (HTTP {e.response.status_code}): {detail}")
    except requests.exceptions.RequestException as e:
        st.error(f"Lỗi kết nối đến backend cho AI: {e}")
    return None
