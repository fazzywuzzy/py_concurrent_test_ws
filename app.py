from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

# Base details
url = "https://api.ws-staging.internal.xfers.com/wallets/0x28d814940527dea24b10726ef0b4c24048b1fd7b/tokens/0x5d6e3cb01dd0bec1f60103d9cc36500f7aa67563/mint"
headers = {
    "Content-Type": "application/json",
    "X-App-Id": "0db21e68f1446557ed65cb8e0c3f408509dcccdc",
    "X-App-Signature": "04c958a55dca1a2b64ba5763f5c2c184761c33d279e320e1940858e963cdaf8c1384a285fd828bbb166be69956b6762147cd4124d51fe90728d280a942139f921b",
}
payload = {
    "amount": "1",
    "return_balances": True
}

# Function to send a single request
def send_request(i):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    idempotency_key = f"mint_morak_user_wallet_failed_in_update_payment_{i:03d}_{timestamp}"
    current_headers = headers.copy()
    current_headers["Idempotency-Key"] = idempotency_key

    try:
        response = requests.post(url, headers=current_headers, json=payload)
        return i, idempotency_key, response.status_code, response.json()
    except Exception as e:
        return i, idempotency_key, -1, str(e)

# Concurrent execution
num_requests = 1000
max_workers = 20

print(f"Starting {num_requests} concurrent requests with {max_workers} workers...")

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(send_request, i) for i in range(1, num_requests + 1)]
    
    # Track success/failure counts
    success_count = 0
    failure_count = 0
    
    for future in as_completed(futures):
        i, idempotency_key, status_code, response_json = future.result()
        if 200 <= status_code < 300:
            success_count += 1
            status = "✅"
        else:
            failure_count += 1
            status = "❌"
            
        print(f"{status} Request {i:03d}: Status {status_code}, Key: {idempotency_key}")

print(f"\nSummary:")
print(f"Total requests: {num_requests}")
print(f"Successful: {success_count}")
print(f"Failed: {failure_count}")