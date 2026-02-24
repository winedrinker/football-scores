import random
import time
from concurrent.futures import ThreadPoolExecutor

import requests


URL = "https://bc5bfjiyu0.execute-api.eu-west-1.amazonaws.com/dev/scores"
TOTAL = 2500
CONCURRENCY = 100

session = requests.Session()

payloads = []
for i in range(TOTAL):
    payloads.append({
        "matchId": 3000 + i,
        "teamHome": "Fradi",
        "teamAway": "Ujpest",
        "score": f"{random.randint(0, 5)}:{random.randint(0, 5)}",
        "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    })


def send(data):
    try:
        r = session.post(URL, json=data, timeout=1)
        return r.status_code
    except:
        return 500


start = time.time()

with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
    results = list(executor.map(send, payloads))

end = time.time()
rps = TOTAL / (end - start)

print(f"\nSummary:")
print(f"Time: {end - start:.2f}s | RPS: {rps:.2f}")
print(f"Success: {results.count(202)}")
