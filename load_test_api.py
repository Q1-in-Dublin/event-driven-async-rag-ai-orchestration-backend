"""
Real load test: fires concurrent requests at the actual POST /slack/events
endpoint with valid Slack signatures.

Unlike the earlier ad-hoc script (parallel `docker exec psql INSERT` +
`redis-cli XADD`), this exercises the real synchronous path FastAPI uses for
every Slack event: verify signature -> save Request to DB -> enqueue to
Redis -> return 202. Since DB-save-then-enqueue happens inside one request
handler, there is no cross-process race condition to hit.

Run from inside the api container (has httpx + settings already configured):
    docker cp load_test_api.py <api-container>:/app/load_test_api.py
    docker-compose exec api python load_test_api.py [concurrency]
"""

import asyncio
import hashlib
import hmac
import json
import sys
import time
import uuid

import httpx

from app.config import settings

API_URL = "http://localhost:8000/slack/events"
CONCURRENCY = int(sys.argv[1]) if len(sys.argv) > 1 else 50

# Nonexistent channel: worker will try Slack chat.postMessage and fail
# gracefully (caught + logged), so this doesn't spam a real channel.
FAKE_CHANNEL = "C_LOADTEST"
FAKE_USER = "U_LOADTEST"


def sign(body: bytes, timestamp: str) -> str:
    basestring = f"v0:{timestamp}:{body.decode()}"
    return "v0=" + hmac.new(
        settings.slack_signing_secret.encode(), basestring.encode(), hashlib.sha256
    ).hexdigest()


async def send_one(client: httpx.AsyncClient, i: int) -> dict:
    payload = {
        "type": "event_callback",
        "event": {
            "user": FAKE_USER,
            "channel": FAKE_CHANNEL,
            # keyword-free text so classify_intent skips the RAG/LLM path
            # entirely -- this test measures queueing, not LLM throughput
            "text": f"load test ping {i} {uuid.uuid4()}",
        },
    }
    body = json.dumps(payload).encode()
    timestamp = str(int(time.time()))
    headers = {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": sign(body, timestamp),
        "Content-Type": "application/json",
    }

    start = time.monotonic()
    try:
        resp = await client.post(API_URL, content=body, headers=headers, timeout=10)
        elapsed = time.monotonic() - start
        data = resp.json() if resp.status_code == 202 else {}
        return {"i": i, "status": resp.status_code, "elapsed": elapsed, "request_id": data.get("request_id")}
    except Exception as e:
        return {"i": i, "status": None, "elapsed": time.monotonic() - start, "error": str(e)}


async def main():
    print(f"Firing {CONCURRENCY} concurrent requests at {API_URL} ...")
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(*(send_one(client, i) for i in range(CONCURRENCY)))

    ok = [r for r in results if r["status"] == 202 and r.get("request_id")]
    failed = [r for r in results if r not in ok]
    elapsed_times = sorted(r["elapsed"] for r in results)

    print(f"\nTotal requests:   {len(results)}")
    print(f"Accepted (202):   {len(ok)}")
    print(f"Failed:           {len(failed)}")
    print(f"Avg latency:      {sum(elapsed_times) / len(elapsed_times) * 1000:.1f} ms")
    print(f"p50 latency:      {elapsed_times[len(elapsed_times) // 2] * 1000:.1f} ms")
    print(f"p99 latency:      {elapsed_times[int(len(elapsed_times) * 0.99)] * 1000:.1f} ms")
    print(f"Max latency:      {max(elapsed_times) * 1000:.1f} ms")

    if failed:
        print("\nFailures:")
        for f in failed[:5]:
            print(f"  {f}")

    with open("/tmp/load_test_request_ids.txt", "w") as f:
        f.write("\n".join(r["request_id"] for r in ok))
    print(f"\n{len(ok)} request_ids written to /tmp/load_test_request_ids.txt")


if __name__ == "__main__":
    asyncio.run(main())
