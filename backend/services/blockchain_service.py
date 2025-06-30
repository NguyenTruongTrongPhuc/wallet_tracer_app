import requests
import time
import logging
from typing import Dict, List

MEMPOOL_API_URL = "https://mempool.space/api"

def fetch_wallet_info(address: str) -> Dict:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: fetch_wallet_info                                   ##
    ##                                                                ##
    ##  - Purpose: To retrieve high-level, aggregate statistics for a ##
    ##    single Bitcoin address from the mempool.space API. This     ##
    ##    includes total received, total sent, and transaction counts.##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The Bitcoin address to query.              ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Constructs the API URL for the specific address.         ##
    ##    2. Makes a GET request to the mempool.space API.            ##
    ##    3. Handles potential HTTP errors and raises an exception    ##
    ##       if the request fails.                                    ##
    ##                                                                ##
    ##  - Output: Returns a dictionary containing the wallet's chain  ##
    ##    statistics, as provided by the API.                         ##
    ##                                                                ##
    ####################################################################
    try:
        response = requests.get(f"{MEMPOOL_API_URL}/address/{address}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Lỗi khi lấy thông tin ví {address}: {e}")
        raise

def fetch_all_transactions(address: str) -> list[dict]:
    ####################################################################
    ##                                                                ##
    ##  FUNCTION: fetch_all_transactions                              ##
    ##                                                                ##
    ##  - Purpose: To fetch the complete transaction history for a    ##
    ##    given Bitcoin address. It handles the API's pagination by   ##
    ##    making multiple requests until all transactions are         ##
    ##    retrieved.                                                  ##
    ##                                                                ##
    ##  - Input:                                                      ##
    ##    - address (str): The Bitcoin address to query.              ##
    ##                                                                ##
    ##  - Process:                                                    ##
    ##    1. Enters a loop that continuously fetches batches of 50    ##
    ##       transactions from the mempool.space API.                 ##
    ##    2. After each successful request, it uses the `txid` of the ##
    ##       last transaction to query the next page (`after_txid`).  ##
    ##    3. A 0.5-second delay (`time.sleep`) is included to prevent ##
    ##       hitting the API's rate limits.                           ##
    ##    4. The loop breaks when the API returns an empty list,      ##
    ##       indicating the end of the transaction history.           ##
    ##                                                                ##
    ##  - Output: Returns a list of dictionaries, where each          ##
    ##    dictionary represents a single transaction.                 ##
    ##                                                                ##
    ####################################################################
    all_txs, last_seen_txid = [], None
    while True:
        try:
            url = f"https://mempool.space/api/address/{address}/txs" + (f"?after_txid={last_seen_txid}" if last_seen_txid else "")
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            txs = response.json()
            if not txs:
                break
            all_txs.extend(txs)
            last_seen_txid = txs[-1]['txid']
            logging.info(f"Đã lấy được {len(txs)} giao dịch cho {address}, tổng: {len(all_txs)}")
            
            time.sleep(0.5)

        except requests.exceptions.RequestException as e:
            logging.error(f"Lỗi khi lấy giao dịch cho {address}: {e}")
            break
    return all_txs