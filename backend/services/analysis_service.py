import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Set

def _label_transaction(tx: Dict) -> str:
    """Gắn nhãn cho giao dịch dựa trên số lượng input và output."""
    vin_count = len(tx.get('vin', []))
    vout_count = len(tx.get('vout', []))

    # Giao dịch Coinbase (đào coin)
    if any(vin.get('is_coinbase', False) for vin in tx.get('vin', [])):
        return "Coinbase (Đào coin)"

    # Giao dịch hợp nhất (nhiều đầu vào, ít đầu ra)
    if vin_count > 5 and vout_count <= 2:
        return "Hợp nhất UTXO"
    
    # Giao dịch phân tán (ít đầu vào, nhiều đầu ra)
    if vin_count <= 2 and vout_count > 5:
        return "Phân tán Coin"

    # Giao dịch phức tạp (có thể là CoinJoin hoặc giao dịch hàng loạt)
    if vin_count > 2 and vout_count > 2:
        return "Giao dịch phức tạp"

    # Giao dịch tiêu chuẩn
    return "Giao dịch tiêu chuẩn"

def _find_clusters(transactions: List[Dict]) -> List[str]:
    """
    Tìm các địa chỉ liên quan dựa trên 'Heuristic Chi Tiêu Chung Đầu Vào'.
    """
    associated_addresses: Set[str] = set()
    for tx in transactions:
        # Bỏ qua giao dịch đào coin
        if any(vin.get('is_coinbase', False) for vin in tx.get('vin', [])):
            continue

        inputs_in_tx = tx.get('vin', [])
        if len(inputs_in_tx) > 1:
            for vin in inputs_in_tx:
                # Đảm bảo 'prevout' và 'scriptpubkey_address' tồn tại
                if vin.get('prevout') and vin['prevout'].get('scriptpubkey_address'):
                    associated_addresses.add(vin['prevout']['scriptpubkey_address'])
    
    return sorted(list(associated_addresses))


def process_and_analyze_data(
    address: str, 
    raw_wallet_info: dict, 
    raw_transactions: list,
    start_date: str, 
    end_date: str
) -> Dict:
    """
    Hàm tổng hợp, xử lý, lọc và phân tích tất cả dữ liệu.
    """
    # 1. Lọc giao dịch theo khoảng thời gian
    df = pd.DataFrame(raw_transactions)
    df['block_time'] = pd.to_datetime(df['status'].apply(lambda x: x.get('block_time')), unit='s', errors='coerce')
    
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date) + timedelta(days=1) # Bao gồm cả ngày kết thúc

    df_filtered = df[(df['block_time'] >= start_dt) & (df['block_time'] <= end_dt)].copy()
    
    # 2. Gắn nhãn và phân tích
    filtered_tx_list = df_filtered.to_dict('records')
    for tx in filtered_tx_list:
        tx['analysis_label'] = _label_transaction(tx)
    
    associated_addresses = _find_clusters(filtered_tx_list)
    # Loại bỏ địa chỉ gốc khỏi danh sách liên quan
    if address in associated_addresses:
        associated_addresses.remove(address)

    # 3. Tính toán các chỉ số tổng hợp
    # Lưu ý: Các chỉ số này từ Blockstream là cho toàn bộ lịch sử, không phải trong khoảng thời gian
    stats = raw_wallet_info.get('chain_stats', {})
    
    analysis_result = {
        "address": address,
        "total_transactions": stats.get('tx_count', 0),
        "total_received": stats.get('funded_txo_sum', 0),
        "total_sent": stats.get('spent_txo_sum', 0),
        "final_balance": stats.get('funded_txo_sum', 0) - stats.get('spent_txo_sum', 0),
        "transactions": filtered_tx_list,
        "associated_addresses": associated_addresses
    }
    
    return analysis_result

