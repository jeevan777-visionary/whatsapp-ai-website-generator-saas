"""Runtime verification: health, auth, project generation (sync), Netlify URL."""
from __future__ import annotations

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("VERIFY_BASE_URL", "http://127.0.0.1:5000")


def main() -> int:
    errors: list[str] = []

  # Health
    r = requests.get(f"{BASE}/health", timeout=10)
    if r.status_code != 200:
        errors.append(f"health failed: {r.status_code}")
    else:
        print("OK /health", r.json())

    email = "verify@wa-ai.local"
    password = "verifypass123"

    # Signup (may 409 if exists)
    r = requests.post(
        f"{BASE}/api/auth/signup",
        json={"email": email, "password": password},
        timeout=15,
    )
    if r.status_code not in (200, 409):
        errors.append(f"signup failed: {r.status_code} {r.text}")

    r = requests.post(
        f"{BASE}/api/auth/login",
        json={"email": email, "password": password},
        timeout=15,
    )
    if r.status_code != 200:
        errors.append(f"login failed: {r.status_code} {r.text}")
        print("FAIL", errors)
        return 1
    token = r.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("OK login")

    r = requests.get(f"{BASE}/api/projects", headers=headers, timeout=15)
    if r.status_code != 200:
        errors.append(f"projects list failed: {r.status_code}")
    else:
        print("OK /api/projects", len(r.json()), "items")

    r = requests.get(f"{BASE}/api/deployments", headers=headers, timeout=15)
    if r.status_code != 200:
        errors.append(f"deployments failed: {r.status_code}")
    else:
        print("OK /api/deployments")

    r = requests.get(f"{BASE}/dashboard/", timeout=15)
    if r.status_code != 200:
        errors.append(f"dashboard failed: {r.status_code}")
    else:
        print("OK /dashboard/")

    # Trigger generation (sync mode)
    msg = "Build a modern luxury restaurant website for Bella Italia with online reservations"
    r = requests.post(
        f"{BASE}/api/projects",
        headers=headers,
        json={"message": msg},
        timeout=300,
    )
    if r.status_code != 200:
        errors.append(f"project create failed: {r.status_code} {r.text}")
    else:
        req_id = r.json().get("request_id")
        print("OK project queued/completed", req_id)
        if os.getenv("SYNC_TASKS", "false").lower() == "true":
            import time

            for _ in range(90):
                pr = requests.get(f"{BASE}/api/projects/{req_id}", headers=headers, timeout=15)
                if pr.status_code == 200:
                    data = pr.json()
                    if data.get("status") == "completed" and data.get("live_url"):
                        print("LIVE URL:", data["live_url"])
                        break
                    if data.get("status") == "failed":
                        errors.append("generation failed")
                        break
                time.sleep(3)

    if errors:
        print("ERRORS:", json.dumps(errors, indent=2))
        return 1
    print("All runtime checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
