import httpx
from fastapi import APIRouter, Query, Body
from datetime import date

# --- SỬA LỖI Ở ĐÂY ---
# Thay thế toàn bộ các đường dẫn tương đối '...' bằng đường dẫn tuyệt đối từ 'backend'
from backend.services import blockchain_service, analysis_service, ai_service
from backend.models.trace_models import WalletAnalysis, AIAnalysisRequest

router = APIRouter()

@router.get("/trace/{address}", response_model=WalletAnalysis)
async def trace_wallet_address(
    address: str,
    start_date: date = Query(..., description="Ngày bắt đầu, định dạng YYYY-MM-DD"),
    end_date: date = Query(..., description="Ngày kết thúc, định dạng YYYY-MM-DD")
):
    """
    Endpoint chính để truy vết một địa chỉ ví.
    Nó tổng hợp các bước: fetch -> analyze -> respond.
    """
    async with httpx.AsyncClient() as client:
        # Fetch raw data in parallel
        raw_info = await blockchain_service.fetch_address_data(client, address)
        raw_txs = await blockchain_service.fetch_transactions_for_address(client, address)
    
    # Analyze data
    analysis_result = analysis_service.process_and_analyze_data(
        address, raw_info, raw_txs, str(start_date), str(end_date)
    )
    
    return analysis_result

@router.post("/analyze-ai")
async def analyze_wallet_with_ai(
    request: AIAnalysisRequest = Body(...)
):
    """
    Endpoint nhận dữ liệu ví và dùng OpenAI để phân tích.
    """
    analysis_content = await ai_service.get_ai_analysis(
        wallet_data=request.wallet_data,
        openai_api_key=request.openai_api_key
    )
    return {"analysis": analysis_content}
