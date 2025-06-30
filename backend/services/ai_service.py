import httpx
import json
from ..core.config import settings

async def get_ai_analysis(wallet_data: dict, openai_api_key: str) -> str:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: get_ai_analysis                                     ##
    ##                                                                ##
    ##  - Purpose: This function is designed for the AI Polling       ##
    ##    feature on the "Monitoring Dashboard" page. It takes        ##
    ##    summarized wallet data and generates a brief, quick         ##
    ##    assessment.                                                 ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - wallet_data (dict): A dictionary containing a summary of  ##
    ##      the wallet's recent activity.                             ##
    ##    - openai_api_key (str): The user's API key for OpenAI.      ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Constructs a short, concise prompt asking the AI to      ##
    ##       identify notable risks or behaviors.                     ##
    ##    2. Sends the request to the OpenAI API (gpt-4-turbo).       ##
    ##    3. Sets a lower `max_tokens` limit for a brief response.    ##
    ##                                                                ##
    ##  - Output: Returns a short string (3-4 lines) with the AI's    ##
    ##    quick assessment of the wallet.                             ##
    ##                                                                ##
    ####################################################################
    wallet_data_str = json.dumps(wallet_data, indent=2, ensure_ascii=False)
    
    prompt_lines = [
        "Bạn là một chuyên gia phân tích on-chain, hãy đưa ra nhận định ngắn gọn (3-4 dòng) về các rủi ro hoặc hành vi đáng chú ý của ví dựa trên dữ liệu tóm tắt sau:",
        "```json",
        wallet_data_str,
        "```"
    ]
    prompt = "\n".join(prompt_lines)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={"model": "gpt-4-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5, "max_tokens": 200},
                timeout=120.0
            )
            response.raise_for_status()
            ai_response = response.json()
            return ai_response['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Lỗi khi gọi AI service (polling): {str(e)}")


async def get_detailed_report(full_analysis_data: dict, openai_api_key: str) -> str:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: get_detailed_report                                 ##
    ##                                                                ##
    ##  - Purpose: This function is designed for the "Generate AI     ##
    ##    Report" feature on the "Wallet Tracer" page. It takes a     ##
    ##    full analysis object and generates an in-depth, multi-      ##
    ##    section intelligence report.                                ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - full_analysis_data (dict): A complete dictionary          ##
    ##      containing all analysis data (stats, red flags, txs...).  ##
    ##    - openai_api_key (str): The user's API key for OpenAI.      ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Truncates the transaction list to keep the prompt        ##
    ##       manageable if it's too long.                             ##
    ##    2. Constructs a highly detailed, structured prompt that     ##
    ##       instructs the AI to act as a senior on-chain financial   ##
    ##       intelligence analyst.                                    ##
    ##    3. Sends the request to the OpenAI API (gpt-4-turbo).       ##
    ##                                                                ##
    ##  - Output: Returns a long, well-formatted Markdown string      ##
    ##    that constitutes the full intelligence report, ready to be  ##
    ##    displayed on the frontend.                                  ##
    ##                                                                ##
    ####################################################################
    if len(full_analysis_data.get('wallet_data', {}).get('transactions', [])) > 15:
        full_analysis_data['wallet_data']['transactions'] = full_analysis_data['wallet_data']['transactions'][:15]
    
    data_str = json.dumps(full_analysis_data, indent=2, ensure_ascii=False)

    prompt_lines = [
        "Bạn là một nhà phân tích tình báo tài chính on-chain (on-chain financial intelligence analyst) cao cấp. Nhiệm vụ của bạn là nhận một báo cáo phân tích kỹ thuật đầy đủ về một ví Bitcoin và chuyển hóa nó thành một bản báo cáo tình báo chi tiết, dễ hiểu, và sâu sắc cho người dùng cuối.",
        "",
        "Dữ liệu phân tích kỹ thuật đầu vào:",
        "```json",
        data_str,
        "```",
        "",
        "**YÊU CẦU BÁO CÁO TÌNH BÁO:**",
        "Dựa tuyệt đối vào dữ liệu được cung cấp, hãy viết một báo cáo chuyên sâu theo cấu trúc sau:",
        "",
        "**Tóm tắt cho Lãnh đạo (Executive Summary):**",
        "(Bắt đầu bằng 2-3 gạch đầu dòng tóm tắt những phát hiện quan trọng nhất.)",
        "",
        "---",
        "",
        "**1. Đánh giá Tổng quan và Hồ sơ Ví:**",
        "- Dựa vào `wallet_profile_classified` và các chỉ số trong `chain_stats`, hãy diễn giải hồ sơ của ví này.",
        "- Phân tích dòng tiền (tổng nhận/gửi) và số dư hiện tại.",
        "",
        "**2. Phân tích Sâu về Rủi ro (Dựa trên Cờ Đỏ):**",
        "- **Đây là phần quan trọng nhất.** Đi qua từng \"cờ đỏ\" (`red_flags`) được phát hiện trong `risk_analysis`.",
        "- Với mỗi loại cờ đỏ, hãy giải thích rõ ý nghĩa và mức độ nghiêm trọng của nó.",
        "",
        "**3. Phân tích các Mẫu Giao dịch Nổi bật:**",
        "- Nhìn vào danh sách `transactions` trong `wallet_data`, có quy luật nào về thời gian, giá trị, hay loại giao dịch không?",
        "",
        "**4. Kết luận và Đề xuất:**",
        "- Đưa ra kết luận cuối cùng về mức độ rủi ro và bản chất hoạt động của ví này.",
        "- Xác nhận lại điểm rủi ro (`risk_score`) và đưa ra đề xuất cụ thể.",
        "",
        "Hãy trình bày báo cáo một cách mạch lạc, chuyên nghiệp, sử dụng định dạng Markdown để làm nổi bật các đề mục."
    ]
    prompt = "\n".join(prompt_lines)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {openai_api_key}"},
                json={"model": "gpt-4-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.4},
                timeout=240.0
            )
            response.raise_for_status()
            ai_response = response.json()
            return ai_response['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Lỗi khi tạo báo cáo AI: {str(e)}")