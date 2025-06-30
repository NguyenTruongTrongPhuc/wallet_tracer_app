import logging
from fastapi import APIRouter, HTTPException
from backend.core.models.trace_models import TraceRequest, FullAnalysisResponse
from backend.services import analysis_service

router = APIRouter()

@router.post("/", response_model=FullAnalysisResponse)
async def trace_wallet(request: TraceRequest) -> FullAnalysisResponse:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: trace_wallet                                        ##
    ##                                                                ##
    ##  - Purpose: This is the main endpoint for the "Wallet Tracer"  ##
    ##    feature. It receives a wallet address and a date range,     ##
    ##    then triggers the full analysis process.                    ##
    ##                                                                ##
    ##  - Input: Receives a POST request to its root path (e.g.,      ##
    ##    /api/v1/trace/). The request body must be a JSON object      ##
    ##    matching the `TraceRequest` model, containing:              ##
    ##    {"address": "...", "start_date": "...", "end_date": "..."}. ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. It validates the incoming request using the              ##
    ##       `TraceRequest` Pydantic model.                           ##
    ##    2. It calls the `perform_full_analysis` function from the   ##
    ##       `analysis_service`, which handles all the heavy lifting. ##
    ##    3. It includes error handling to catch any exceptions       ##
    ##       during the analysis and returns an appropriate HTTP      ##
    ##       error.                                                   ##
    ##                                                                ##
    ##  - Output: On success, it returns a `FullAnalysisResponse`     ##
    ##    object, which FastAPI automatically converts to a JSON      ##
    ##    response containing the complete wallet analysis.           ##
    ##                                                                ##
    ####################################################################
    try:
        analysis_result = analysis_service.perform_full_analysis(
            address=request.address,
            start_date_str=request.start_date,
            end_date_str=request.end_date
        )
        return analysis_result
    except Exception as e:
        logging.error(f"Lỗi endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Lỗi máy chủ nội bộ khi phân tích: {e}")