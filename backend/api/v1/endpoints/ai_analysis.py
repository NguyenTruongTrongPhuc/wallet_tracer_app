from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from ....core.config import settings
from ....services import blockchain_service, analysis_service, ai_service
from ....core.models.trace_models import FullAnalysisResponse

router = APIRouter()

# --- Common model for AI responses ---
class AIResponse(BaseModel):
    analysis_text: str

# --- Endpoint for Polling (Monitoring Page) ---
class AIPollingRequest(BaseModel):
    address: str

@router.post("/poll", response_model=AIResponse)
async def get_polling_ai_analysis(request: AIPollingRequest):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: get_polling_ai_analysis                             ##
    ##                                                                ##
    ##  - Purpose: This endpoint is designed for the AI Polling       ##
    ##    feature on the "Monitoring Dashboard" page. It performs a   ##
    ##    quick and lightweight analysis periodically.                ##
    ##                                                                ##
    ##  - Input: Receives a POST request to /api/v1/ai/poll with a   ##
    ##    JSON body containing the wallet address: {"address": "..."}.##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Retrieves the OpenAI API Key from server configuration.  ##
    ##    2. Calls services to get summary data for the wallet.       ##
    ##    3. Sends that summary data to the AI for a quick assessment.##
    ##                                                                ##
    ##  - Output: Returns a JSON object containing the AI's short     ##
    ##    assessment: {"analysis_text": "..."}.                       ##
    ##                                                                ##
    ####################################################################
    openai_api_key = settings.OPENAI_API_KEY
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured on the server.")
    
    try:
       
        wallet_info = await run_in_threadpool(blockchain_service.fetch_wallet_info, request.address)
        transactions = await run_in_threadpool(blockchain_service.fetch_all_transactions, request.address)
        
        summary_data = {
            "wallet_summary": {
                "address": request.address,
                "total_transactions": wallet_info.get('chain_stats', {}).get('tx_count', 0),
                "final_balance_btc": (wallet_info.get('chain_stats', {}).get('funded_txo_sum', 0) - wallet_info.get('chain_stats', {}).get('spent_txo_sum', 0)) / 1e8,
            },
            "recent_transactions": [
                {"value_btc": sum(out.get('value', 0) for out in tx.get('vout', [])) / 1e8, "transaction_label": analysis_service.classify_transaction_label(tx)} for tx in transactions[:15]
            ]
        }
        analysis_result = await ai_service.get_ai_analysis(summary_data, openai_api_key)
        return AIResponse(analysis_text=analysis_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi polling AI: {str(e)}")


class AIReportRequest(BaseModel):
    address: str
    start_date: str
    end_date: str

class AIReportResponse(BaseModel):
    report_text: str

@router.post("/report", response_model=AIReportResponse)
async def generate_ai_report(request: AIReportRequest):
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: generate_ai_report                                  ##
    ##                                                                ##
    ##  - Purpose: This endpoint is designed for the "Generate AI     ##
    ##    Report" feature on the "Wallet Tracer" page. It performs a  ##
    ##    full and in-depth analysis.                                 ##
    ##                                                                ##
    ##  - Input: Receives a POST request to /api/v1/ai/report with a ##
    ##    JSON body containing the address and time range:            ##
    ##    {"address": "...", "start_date": "...", "end_date": "..."}. ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. The backend re-runs the `perform_full_analysis` function ##
    ##       to get all detailed data (stats, red flags, txs...).     ##
    ##    2. This entire block of detailed data is sent to the AI to  ##
    ##       write an in-depth report.                                ##
    ##                                                                ##
    ##  - Output: Returns a JSON object containing the AI's detailed  ##
    ##    report: {"analysis_text": "..."}.                           ##
    ##                                                                ##
    ####################################################################
    openai_api_key = settings.OPENAI_API_KEY
    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured.")
    
    try:
        full_analysis_data = await run_in_threadpool(
            analysis_service.perform_full_analysis,
            address=request.address,
            start_date_str=request.start_date,
            end_date_str=request.end_date
        )
        
        analysis_dict = full_analysis_data.model_dump()
        report_result = await ai_service.get_detailed_report(analysis_dict, openai_api_key)
        
        return AIReportResponse(report_text=report_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ khi tạo báo cáo AI: {str(e)}")