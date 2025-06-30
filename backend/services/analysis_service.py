import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from pydantic import TypeAdapter
from backend.services import blockchain_service
from backend.core.models.trace_models import (
    Transaction, 
    WalletAnalysis,
    RiskAnalysis,
    FullAnalysisResponse
)

BTC_PRICE_USD = 65000
TRANSACTION_THRESHOLD_USD = 10000

def classify_wallet_profile(stats: Dict, red_flags: Dict) -> str:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: classify_wallet_profile                             ##
    ##                                                                ##
    ##  - Purpose: To assign a high-level profile category to a       ##
    ##    wallet based on its overall statistics (balance, transaction##
    ##    count) and the presence of any detected red flags.          ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - stats (dict): A dictionary with chain statistics like     ##
    ##      'funded_txo_sum', 'spent_txo_sum', and 'tx_count'.        ##
    ##    - red_flags (dict): The dictionary of detected red flags.   ##
    ##                                                                ##
    ##  - Output: Returns a string label for the wallet profile,      ##
    ##    e.g., "🐳 Cá Voi (Whale)", "🔄 Ví Giao Dịch Tần Suất Cao   ##
    ##    (Trader)".                                                  ##
    ##                                                                ##
    ####################################################################
    balance_sats = stats.get('funded_txo_sum', 0) - stats.get('spent_txo_sum', 0)
    balance_btc = balance_sats / 1e8
    tx_count = stats.get('tx_count', 0)
    if balance_btc >= 1000: return "🐳 Cá Voi (Whale)"
    if balance_btc >= 100 and tx_count < 50: return "💰 Ví Tích Lũy Lớn (Large Holder)"
    if tx_count >= 500: return "🔄 Ví Giao Dịch Tần Suất Cao (Trader)"
    if has_red_flags(red_flags): return "⚠️ Ví Có Dấu Hiệu Rủi Ro"
    return "👤 Ví Tiêu Chuẩn (Standard Wallet)"

def has_red_flags(red_flags: Dict) -> bool:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: has_red_flags                                       ##
    ##                                                                ##
    ##  - Purpose: A simple helper function to quickly determine if   ##
    ##    any significant red flags were found during the analysis.   ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - red_flags (dict): The dictionary of detected red flags.   ##
    ##                                                                ##
    ##  - Output: Returns a boolean value: `True` if any red flag     ##
    ##    list is not empty or a flag dictionary has a positive       ##
    ##    count, `False` otherwise.                                   ##
    ##                                                                ##
    ####################################################################
    return any(
        (isinstance(v, list) and len(v) > 0) or (isinstance(v, dict) and v.get('count', 0) > 0)
        for k, v in red_flags.items()
    )

def classify_transaction_label(tx_dict: Dict) -> str:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: classify_transaction_label                          ##
    ##                                                                ##
    ##  - Purpose: To apply a heuristic-based label to a single       ##
    ##    transaction by analyzing its structure (the number of       ##
    ##    inputs and outputs).                                        ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - tx_dict (dict): A dictionary representing one transaction.##
    ##                                                                ##
    ##  - Output: Returns a string label describing the transaction's ##
    ##    pattern, such as "Peel Chain", "Gom Coin" (Consolidation),  ##
    ##    "Phân Tán" (Distribution), or "Phức Tạp" (Complex).         ##
    ##                                                                ##
    ####################################################################
    vins = [v for v in tx_dict.get('vin', []) if isinstance(v, dict)]
    vouts = [v for v in tx_dict.get('vout', []) if isinstance(v, dict)]
    if len(vins) == 1 and len(vouts) == 2: return "Peel Chain"
    if len(vins) >= 5 and len(vouts) == 1: return "Gom Coin"
    if len(vins) == 1 and len(vouts) >= 5: return "Phân Tán"
    if len(vins) > 2 and len(vouts) > 2: return "Phức Tạp"
    return "Tiêu Chuẩn"

def detect_high_value_tx(transactions: List[Dict], threshold_usd: float = TRANSACTION_THRESHOLD_USD, btc_price_usd: float = BTC_PRICE_USD) -> List[Dict]:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: detect_high_value_tx                                ##
    ##                                                                ##
    ##  - Purpose: To scan a list of transactions and identify any    ##
    ##    that exceed a predefined value threshold (in USD).          ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts.   ##
    ##    - threshold_usd (float): The value limit in USD.            ##
    ##    - btc_price_usd (float): The current BTC price to use for   ##
    ##      conversion.                                               ##
    ##                                                                ##
    ##  - Output: Returns a list of dictionaries. Each dictionary     ##
    ##    represents a flagged transaction, containing its `txid` and ##
    ##    the reason for being flagged.                               ##
    ##                                                                ##
    ####################################################################
    high_value_txs = []
    threshold_sats = int((threshold_usd / btc_price_usd) * 1e8)
    for tx in transactions:
        total_out_value = sum(vout.get('value', 0) or 0 for vout in tx.get('vout', []))
        if total_out_value >= threshold_sats:
            high_value_txs.append({ "txid": tx.get('txid'), "reason": f"Tổng giá trị {total_out_value/1e8:.4f} BTC (~${(total_out_value/1e8)*btc_price_usd:,.0f}) vượt ngưỡng." })
    return high_value_txs

def detect_peel_chains(transactions: List[Dict], original_address: str) -> List[Dict]:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: detect_peel_chains                                  ##
    ##                                                                ##
    ##  - Purpose: To detect a specific transaction pattern known as  ##
    ##    a "peel chain," which is often associated with payments     ##
    ##    from a large UTXO, where a small amount is "peeled" off.    ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts.   ##
    ##    - original_address (str): The main wallet address being     ##
    ##      analyzed.                                                 ##
    ##                                                                ##
    ##  - Output: Returns a list of flagged transactions (dicts) that ##
    ##    match the peel chain heuristic.                             ##
    ##                                                                ##
    ####################################################################
    peel_chains = []
    for tx in transactions:
        vins = [v for v in tx.get('vin', []) if isinstance(v, dict)]
        vouts = [v for v in tx.get('vout', []) if isinstance(v, dict)]
        vin_addresses = {vin.get('prevout', {}).get('scriptpubkey_address') for vin in vins if vin.get('prevout')}
        if len(vin_addresses) == 1 and original_address in vin_addresses and len(vouts) == 2:
            outputs = sorted(vouts, key=lambda x: x.get('value', 0) or 0)
            if len(outputs) == 2 and outputs[0].get('value', 0) and outputs[1].get('value', 0) > (outputs[0].get('value', 0)) * 9:
                peel_chains.append({"txid": tx.get('txid'), "reason": "1 vào, 2 ra, 1 đầu ra lớn hơn nhiều."})
    return peel_chains

def detect_structuring(transactions: List[Dict], threshold_usd: float = 9500, btc_price_usd: float = BTC_PRICE_USD) -> List[Dict]:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: detect_structuring                                  ##
    ##                                                                ##
    ##  - Purpose: To detect transactions with values that are close  ##
    ##    to a financial reporting threshold (e.g., just under        ##
    ##    $10,000). This pattern, known as structuring or smurfing,   ##
    ##    can indicate an attempt to avoid regulatory scrutiny.       ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts.   ##
    ##                                                                ##
    ##  - Output: Returns a list of flagged transactions (dicts) that ##
    ##    fall within the suspicious value range.                     ##
    ##                                                                ##
    ####################################################################
    structuring_txs = []
    lower_bound_sats = int((threshold_usd * 0.9 / btc_price_usd) * 1e8)
    upper_bound_sats = int((threshold_usd * 1.05 / btc_price_usd) * 1e8)
    for tx in transactions:
        total_value = sum(vout.get('value', 0) or 0 for vout in tx.get('vout', []))
        if lower_bound_sats < total_value < upper_bound_sats:
            structuring_txs.append({"txid": tx.get('txid'), "reason": f"Giá trị gần ngưỡng giám sát (${threshold_usd:,.0f})."})
    return structuring_txs

def detect_mimo_tx(transactions: List[Dict], input_threshold: int = 3, output_threshold: int = 3) -> List[Dict]:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: detect_mimo_tx                                      ##
    ##                                                                ##
    ##  - Purpose: To detect complex transactions with Multiple-      ##
    ##    Inputs and Multiple-Outputs (MIMO). Such transactions can   ##
    ##    be used to obfuscate the flow of funds, similar to          ##
    ##    a coinjoin.                                                 ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts.   ##
    ##    - input_threshold (int): Min number of inputs to flag.      ##
    ##    - output_threshold (int): Min number of outputs to flag.    ##
    ##                                                                ##
    ##  - Output: Returns a list of flagged transactions (dicts) that ##
    ##    meet the MIMO criteria.                                     ##
    ##                                                                ##
    ####################################################################
    mimo_txs = []
    for tx in transactions:
        vin_count, vout_count = len(tx.get('vin', [])), len(tx.get('vout', []))
        if vin_count >= input_threshold and vout_count >= output_threshold:
            mimo_txs.append({"txid": tx.get('txid'), "reason": f"{vin_count} vào, {vout_count} ra."})
    return mimo_txs

def analyze_address_reuse(transactions: List[Dict], original_address: str) -> Dict[str, Any]:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: analyze_address_reuse                               ##
    ##                                                                ##
    ##  - Purpose: To analyze how often the original address is       ##
    ##    reused as an input in subsequent transactions. Address      ##
    ##    reuse is a poor privacy practice that links multiple        ##
    ##    transactions together.                                      ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - transactions (List[dict]): A list of transaction dicts.   ##
    ##    - original_address (str): The main wallet address.          ##
    ##                                                                ##
    ##  - Output: Returns a dictionary containing the reuse count,    ##
    ##    total transactions, and a qualitative verdict ("Ít" for     ##
    ##    "Low" or "Thường xuyên" for "Frequent").                    ##
    ##                                                                ##
    ####################################################################
    reuse_count = sum(1 for tx in transactions if any(vin.get('prevout', {}).get('scriptpubkey_address') == original_address for vin in tx.get('vin', []) if vin.get('prevout')))
    verdict, reason = ("Ít", "Không có dấu hiệu tái sử dụng địa chỉ bất thường.")
    total_txs = len(transactions)
    if total_txs > 5 and (total_txs > 0 and (reuse_count / total_txs) > 0.3):
        verdict, reason = ("Thường xuyên", f"Địa chỉ được tái sử dụng trong {reuse_count}/{total_txs} giao dịch.")
    return {"count": reuse_count, "total_txs": total_txs, "verdict": verdict, "reason": reason}

def perform_full_analysis(address: str, start_date_str: str, end_date_str: str) -> FullAnalysisResponse:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: perform_full_analysis                               ##
    ##                                                                ##
    ##  - Purpose: This is the main orchestrator function of the      ##
    ##    service. It fetches all necessary on-chain data, runs all   ##
    ##    the individual analysis functions (heuristics), and         ##
    ##    aggregates the results into a single, comprehensive         ##
    ##    response object.                                            ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The Bitcoin address to analyze.            ##
    ##    - start_date_str (str): The start of the analysis period.   ##
    ##    - end_date_str (str): The end of the analysis period.       ##
    ##                                                                ##
    ##  - Output: Returns a `FullAnalysisResponse` Pydantic model     ##
    ##    object, which contains the complete, structured analysis    ##
    ##    of the wallet.                                              ##
    ##                                                                ##
    ####################################################################
    raw_wallet_info = blockchain_service.fetch_wallet_info(address)
    raw_transactions = blockchain_service.fetch_all_transactions(address)

    df = pd.DataFrame([tx for tx in raw_transactions if isinstance(tx, dict)])
    filtered_tx_list = []
    if not df.empty and 'status' in df.columns:
        df['block_time'] = pd.to_datetime(df['status'].apply(lambda x: x.get('block_time')), unit='s', errors='coerce')
        df.dropna(subset=['block_time'], inplace=True)
        start_dt = pd.to_datetime(start_date_str)
        end_dt = pd.to_datetime(end_date_str) + timedelta(days=1)
        df_filtered = df[(df['block_time'] >= start_dt) & (df['block_time'] < end_dt)].copy()
        filtered_tx_list = df_filtered.to_dict('records')

    tx_dicts_for_parsing = []
    for tx_dict in filtered_tx_list:
        value_in = sum(vout.get('value', 0) for vout in tx_dict.get('vout', []) if vout.get('scriptpubkey_address') == address)
        value_out = sum(vin.get('prevout', {}).get('value', 0) for vin in tx_dict.get('vin', []) if vin.get('prevout') and vin.get('prevout', {}).get('scriptpubkey_address') == address)
        tx_dict['balance_delta'] = value_in - value_out
        tx_dict['total_value'] = sum(vout.get('value', 0) for vout in tx_dict.get('vout', []))
        tx_dict['transaction_label'] = classify_transaction_label(tx_dict)
        if 'block_time' in tx_dict and pd.notna(tx_dict['block_time']):
            tx_dict['block_time_iso'] = tx_dict['block_time'].isoformat()
        tx_dicts_for_parsing.append(tx_dict)

    TransactionListAdapter = TypeAdapter(List[Transaction])
    enriched_txs = TransactionListAdapter.validate_python(tx_dicts_for_parsing)
    
    enriched_tx_dicts = [tx.model_dump() for tx in enriched_txs]

    red_flags = {
        "high_value_transactions": detect_high_value_tx(enriched_tx_dicts),
        "peel_chains": detect_peel_chains(enriched_tx_dicts, address),
        "structuring_transactions": detect_structuring(enriched_tx_dicts),
        "complex_mimo_transactions": detect_mimo_tx(enriched_tx_dicts),
        "address_reuse": analyze_address_reuse(enriched_tx_dicts, address)
    }
    
    risk_score_value = sum(len(v) for v in red_flags.values() if isinstance(v, list))
    if red_flags["address_reuse"]["verdict"] == "Thường xuyên":
        risk_score_value += 1
    risk_score = min(risk_score_value * 15, 100)
    
    profile = "Rủi Ro Thấp"
    if risk_score > 60: profile = "Rủi Ro Cao"
    elif risk_score > 30: profile = "Rủi Ro Trung Bình"

    risk_analysis_obj = RiskAnalysis(risk_score=risk_score, profile=profile, red_flags=red_flags)
    
    stats = raw_wallet_info.get('chain_stats', {})
    wallet_analysis_obj = WalletAnalysis(
        address=address,
        total_transactions=stats.get('tx_count', 0),
        total_received=stats.get('funded_txo_sum', 0),
        total_sent=stats.get('spent_txo_sum', 0),
        final_balance=stats.get('funded_txo_sum', 0) - stats.get('spent_txo_sum', 0),
        transactions=enriched_txs,
    )
    
    return FullAnalysisResponse(
        wallet_data=wallet_analysis_obj,
        risk_analysis=risk_analysis_obj,
        wallet_profile_classified=classify_wallet_profile(stats, red_flags),
        chain_stats=stats
    )