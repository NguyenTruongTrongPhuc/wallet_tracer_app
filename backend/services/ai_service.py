import httpx
from fastapi import HTTPException
from ..core.config import settings
from ..models.trace_models import WalletAnalysis

async def get_ai_analysis(wallet_data: WalletAnalysis, openai_api_key: str) -> str:
    """Gửi dữ liệu đến OpenAI và nhận lại phân tích."""
    
    # Cắt bớt dữ liệu để không vượt quá giới hạn token
    wallet_data_dict = wallet_data.dict()
    if 'transactions' in wallet_data_dict and len(wallet_data_dict['transactions']) > 15:
        wallet_data_dict['transactions'] = wallet_data_dict['transactions'][:15]

    prompt = f"""
    Bạn là một chuyên gia phân tích blockchain và điều tra viên tài chính tiền điện tử với 10 năm kinh nghiệm.
    Nhiệm vụ của bạn là phân tích dữ liệu JSON của một ví Bitcoin và đưa ra những nhận định chuyên sâu, sắc bén.

    Dưới đây là dữ liệu của ví:
    ```json
    {wallet_data_dict}
    ```

    Dựa vào dữ liệu trên, hãy thực hiện phân tích chi tiết theo các mục sau:
    1.  **Tổng quan về hoạt động (Wallet Profile):**
        * Đây có phải là một ví hoạt động tích cực không? Dựa vào số lượng giao dịch trong khoảng thời gian được cung cấp.
        * Tóm tắt dòng tiền chính (tổng nhận, tổng gửi). Có sự chênh lệch lớn bất thường không?

    2.  **Phân tích Mẫu Giao Dịch (Transaction Patterns):**
        * Dựa vào `analysis_label`, hãy nhận xét các loại giao dịch chính của ví này (Hợp nhất, Phân tán, v.v.).
        * Có các giao dịch với giá trị lớn bất thường không?
        * Có dấu hiệu của "peeling chain" (chuỗi lột vỏ) không?

    3.  **Phân tích Cụm Ví (Cluster Analysis):**
        * Ví này có liên kết với các địa chỉ nào khác (`associated_addresses`) không? Điều này có ý nghĩa gì? Nó cho thấy các địa chỉ này có thể thuộc cùng một chủ sở hữu.

    4.  **Cờ Đỏ & Rủi Ro Tiềm Ẩn (Red Flags & Potential Risks):**
        * Dựa trên các mẫu hình, có dấu hiệu nào liên quan đến các hoạt động rủi ro như mixer (trộn coin), cờ bạc, hoặc các dịch vụ darknet không? (Lưu ý: đây chỉ là phỏng đoán).
        * Ví có xu hướng tích lũy hay phân phối?

    5.  **Đánh giá tổng kết:** Đưa ra một kết luận ngắn gọn về "sức khỏe" và mức độ rủi ro của ví này. Xếp hạng rủi ro theo thang điểm: Thấp, Trung bình, Cao.

    Hãy trình bày câu trả lời bằng tiếng Việt, sử dụng định dạng Markdown rõ ràng.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OPENAI_API_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                },
                timeout=90.0
            )
            response.raise_for_status()
            ai_response = response.json()
            return ai_response['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Lỗi từ API của OpenAI: {e.response.text}")
