import httpx
from fastapi import HTTPException
from ..core.config import settings

async def fetch_address_data(client: httpx.AsyncClient, address: str) -> dict:
    """Lấy thông tin cơ bản của một địa chỉ."""
    try:
        response = await client.get(f"{settings.BLOCKCHAIN_API_URL}/address/{address}")
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404 or e.response.status_code == 400:
            raise HTTPException(status_code=404, detail=f"Địa chỉ ví không hợp lệ hoặc không tìm thấy: {address}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Lỗi từ API Blockchain khi lấy thông tin ví: {e.response.text}")

async def fetch_transactions_for_address(client: httpx.AsyncClient, address: str) -> list:
    """Lấy tất cả các giao dịch của một địa chỉ."""
    try:
        # Blockstream API trả về 25 giao dịch mỗi lần. Cần lặp để lấy hết.
        all_txs = []
        last_txid = None
        while True:
            url = f"{settings.BLOCKCHAIN_API_URL}/address/{address}/txs"
            if last_txid:
                url += f"/chain/{last_txid}"
            
            response = await client.get(url)
            response.raise_for_status()
            txs_batch = response.json()
            
            if not txs_batch:
                break
            
            all_txs.extend(txs_batch)
            last_txid = txs_batch[-1]['txid']
            # Giới hạn để tránh request quá nhiều trong môi trường demo
            if len(all_txs) > 100: 
                break
        
        return all_txs
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Lỗi từ API Blockchain khi lấy giao dịch: {e.response.text}")
