from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class TransactionVin(BaseModel):
    txid: Optional[str] = None
    vout: Optional[int] = None
    prevout: Optional[Dict[str, Any]] = None
    scriptsig: Optional[str] = None
    scriptsig_asm: Optional[str] = None
    is_coinbase: bool
    sequence: int

class TransactionVout(BaseModel):
    scriptpubkey: str
    scriptpubkey_asm: str
    scriptpubkey_type: str
    scriptpubkey_address: Optional[str] = None
    value: int

class Transaction(BaseModel):
    txid: str
    version: int
    locktime: int
    vin: List[TransactionVin]
    vout: List[TransactionVout]
    size: int
    weight: int
    fee: int
    status: Dict[str, Any]
    balance_delta: Optional[int] = None
    total_value: Optional[int] = None
    transaction_label: Optional[str] = None
    block_time_iso: Optional[str] = None

class WalletAnalysis(BaseModel):
    address: str
    total_transactions: int
    total_received: int
    total_sent: int
    final_balance: int
    transactions: List[Transaction]
    associated_addresses: Optional[List[str]] = None

class AIAnalysisRequest(BaseModel):
    wallet_data: WalletAnalysis
    openai_api_key: str
    
class RiskAnalysis(BaseModel):
    risk_score: int
    profile: str
    red_flags: Dict[str, Any]

class FullAnalysisResponse(BaseModel):
    wallet_data: WalletAnalysis
    risk_analysis: RiskAnalysis
    wallet_profile_classified: str
    chain_stats: Dict[str, Any]

class TraceRequest(BaseModel):
    address: str
    start_date: str
    end_date: str