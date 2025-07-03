import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1")

def get_analysis_results(address: str, start_date: str, end_date: str) -> dict:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: get_analysis_results                                ##
    ##                                                                ##
    ##  - Purpose: This function acts as the primary bridge for the   ##
    ##    "Wallet Tracer" page. It sends a request to the backend to  ##
    ##    perform a full, detailed analysis of a specific wallet      ##
    ##    within a given date range.                                  ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The Bitcoin address to be analyzed.        ##
    ##    - start_date (str): The start date for the analysis period. ##
    ##    - end_date (str): The end date for the analysis period.     ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Constructs the full API endpoint URL (/api/v1/trace/).   ##
    ##    2. Creates a JSON payload with the address and dates.       ##
    ##    3. Sends a POST request to the backend.                     ##
    ##    4. Handles potential HTTP and network errors, raising a     ##
    ##       clear exception if the backend returns an error.         ##
    ##                                                                ##
    ##  - Output: On success, returns a dictionary containing the     ##
    ##    complete analysis data (`FullAnalysisResponse`).            ##
    ##                                                                ##
    ####################################################################
    trace_endpoint = f"{BACKEND_URL}/trace/"
    payload = {"address": address, "start_date": start_date, "end_date": end_date}
    try:
        response = requests.post(trace_endpoint, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Lỗi từ server: {e.response.json().get('detail', e.response.text)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến backend: {e}")

def get_polling_ai_analysis(address: str) -> dict:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: get_polling_ai_analysis                             ##
    ##                                                                ##
    ##  - Purpose: This function supports the AI Polling feature on   ##
    ##    the "Monitoring Dashboard". It requests a quick, summary-   ##
    ##    based AI analysis from the backend.                         ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The specific Bitcoin address to get an     ##
    ##      AI assessment for.                                        ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Constructs the API URL for the polling endpoint          ##
    ##       (/api/v1/ai/poll/).                                      ##
    ##    2. Sends a POST request with just the address.              ##
    ##                                                                ##
    ##  - Output: Returns a dictionary containing the short AI-       ##
    ##    generated text: {"analysis_text": "..."}.                   ##
    ##                                                                ##
    ####################################################################
    ai_endpoint = f"{BACKEND_URL}/ai/poll/"
    payload = {"address": address}
    try:
        response = requests.post(ai_endpoint, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Lỗi từ server khi phân tích AI: {e.response.json().get('detail', e.response.text)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến backend cho phân tích AI: {e}")


def generate_ai_report(address: str, start_date: str, end_date: str) -> dict:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: generate_ai_report                                  ##
    ##                                                                ##
    ##  - Purpose: This function supports the "Generate AI Report"    ##
    ##    feature on the "Wallet Tracer" page. It initiates the       ##
    ##    creation of a full, in-depth intelligence report.           ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The wallet address for the report.         ##
    ##    - start_date (str): The start date for the report's data.   ##
    ##    - end_date (str): The end date for the report's data.       ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Constructs the API URL for the report generation         ##
    ##       endpoint (/api/v1/ai/report/).                           ##
    ##    2. Sends a POST request with the address and date range.    ##
    ##       The backend will handle the heavy data fetching and      ##
    ##       analysis internally.                                     ##
    ##                                                                ##
    ##  - Output: Returns a dictionary containing the full,           ##
    ##    Markdown-formatted AI report: {"report_text": "..."}.       ##
    ##                                                                ##
    ####################################################################

    ai_endpoint = f"{BACKEND_URL}/ai/report/"
    

    payload = {
        "address": address,
        "start_date": start_date,
        "end_date": end_date
    }
    
    try:
        response = requests.post(ai_endpoint, json=payload, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise Exception(f"Lỗi từ server khi tạo báo cáo AI: {e.response.json().get('detail', e.response.text)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến backend cho báo cáo AI: {e}")
    
def send_wallet_address(address: str):
    """Gửi địa chỉ ví đến backend để xử lý."""
    api_url = f"{BACKEND_URL}/auth/login/web3"
    try:
        response = requests.post(
            api_url,
            json={"address": address},
            timeout=30 # Thêm timeout để tránh chờ đợi quá lâu
        )
        response.raise_for_status()  # Dòng này sẽ báo lỗi nếu status code là 4xx hoặc 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        # Bắt các lỗi liên quan đến network hoặc HTTP status code
        print(f"Lỗi khi gọi API {api_url}: {e}")
        # Bạn có thể trả về một dictionary lỗi để xử lý ở giao diện
        return {"status": "error", "message": str(e)}
