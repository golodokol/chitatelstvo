#!/usr/bin/env python3
import json
import urllib.request

body = json.dumps(
    {
        "parent_name": "Audit",
        "parent_email": "audit@example.com",
        "child_name": "Test",
        "notification_channel": "email",
        "module_id": 5,
        "chosen_stage": "1",
    }
).encode()

req = urllib.request.Request(
    "http://127.0.0.1:8000/webhook/register",
    data=body,
    headers={
        "Content-Type": "application/json",
        "X-Webhook-Secret": "kiaxd8uU3nbdDHaxJaDtDDMG7BM4zohIAw2JTNaDRlgx",
    },
    method="POST",
)
try:
    resp = urllib.request.urlopen(req, timeout=30)
    print("status:", resp.status)
    print(resp.read().decode()[:800])
except urllib.error.HTTPError as exc:
    print("status:", exc.code)
    print(exc.read().decode()[:800])
