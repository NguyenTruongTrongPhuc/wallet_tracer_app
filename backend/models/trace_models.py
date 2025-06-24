from pydantic import BaseModel
from typing import List, Optional, Any

class TransactionVin(BaseModel):
    txid: Optional[str] = None
    vout: Optional[int] = None
    prevout: Optional[Any] = None
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
    status: Any
    
    analysis_label: Optional[str] = None

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
