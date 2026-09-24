#!/usr/bin/env python3
"""
scripts/stress_test.py
Multi-threaded load & stress testing tool for Maison Luxé AI Stylist (STELLA).
Simulates concurrent user sessions against the live deployed ECS Fargate service.
Reads configuration & tokens from environment variables or .env file.
"""
import argparse
import json
import os
import threading
import time
import urllib.request
from pathlib import Path

# Automatically load .env file if present
def load_env_file():
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip("'\""))

load_env_file()

DEFAULT_URL = os.getenv("CHAT_API_URL", "https://predictoraa.com/chat")
DEFAULT_AUTH_URL = os.getenv("AUTH_USERS_URL", "https://predictoraa.com/auth/users")
DEFAULT_CONCURRENT_USERS = int(os.getenv("CONCURRENT_USERS", "5"))
DEFAULT_MESSAGE = "Recommend luxury silk evening dresses under $600 with matching accessories"


def get_jwt_token(auth_url: str) -> str:
    """
    Retrieves JWT token:
    1. Checks environment variable JWT_TOKEN or AUTH_TOKEN (from .env)
    2. If not found, dynamically fetches a fresh signed token from the live auth endpoint.
    """
    env_token = os.getenv("JWT_TOKEN") or os.getenv("AUTH_TOKEN")
    if env_token:
        print("🔑 Loaded JWT token from environment / .env file.")
        return env_token

    print(f"🌐 Fetching fresh JWT token dynamically from {auth_url}...")
    try:
        req = urllib.request.Request(auth_url, headers={"User-Agent": "MaisonLuxeStressTester/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            token = data["users"][0]["token"]
            user_name = data["users"][0].get("name", "Demo User")
            print(f"✅ Successfully acquired live JWT token for: {user_name}")
            return token
    except Exception as e:
        raise RuntimeError(f"❌ Failed to acquire JWT token from {auth_url}: {e}")


def send_chat_request(user_id: int, url: str, token: str, message: str, results: list):
    """Sends a single authenticated chat request and tracks latency."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = json.dumps({
        "message": message,
        "session_id": f"stress_test_user_{user_id}",
    }).encode()

    start_time = time.time()
    print(f"🚀 [User {user_id}] Dispatched chat request...")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            latency = time.time() - start_time
            print(f"✅ [User {user_id}] HTTP {resp.status} in {latency:.2f}s")
            results.append({"user_id": user_id, "status": resp.status, "latency": latency, "error": None})
    except Exception as e:
        latency = time.time() - start_time
        print(f"❌ [User {user_id}] Failed after {latency:.2f}s: {e}")
        results.append({"user_id": user_id, "status": 500, "latency": latency, "error": str(e)})


def main():
    parser = argparse.ArgumentParser(description="Maison Luxé AI Stylist Stress Testing Tool")
    parser.add_argument("-u", "--users", type=int, default=DEFAULT_CONCURRENT_USERS, help="Number of concurrent virtual users (default: 5)")
    parser.add_argument("-url", "--target-url", type=str, default=DEFAULT_URL, help="Target Chat URL")
    args = parser.parse_args()

    print(f"\n=======================================================")
    print(f"   MAISON LUXÉ (STELLA) LOAD TESTER")
    print(f"   Target: {args.target_url}")
    print(f"   Concurrent Virtual Users: {args.users}")
    print(f"=======================================================\n")

    token = get_jwt_token(DEFAULT_AUTH_URL)
    results = []

    start_wall_clock = time.time()
    threads = [
        threading.Thread(
            target=send_chat_request,
            args=(i + 1, args.target_url, token, DEFAULT_MESSAGE, results),
        )
        for i in range(args.users)
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total_time = time.time() - start_wall_clock
    success_count = sum(1 for r in results if r["status"] == 200)
    avg_latency = sum(r["latency"] for r in results) / len(results) if results else 0

    print(f"\n-------------------------------------------------------")
    print(f"   SUMMARY RESULTS")
    print(f"   Total Requests Sent : {len(results)}")
    print(f"   Successful (200 OK) : {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    print(f"   Average Latency     : {avg_latency:.2f}s")
    print(f"   Total Duration      : {total_time:.2f}s")
    print(f"-------------------------------------------------------\n")


if __name__ == "__main__":
    main()
