"""最小连通性 + 中文首测：1 段中文 state + 2 个 noul（关键词 vs 虚词对照）。"""
import json
import time
import urllib.request

KEY = open("jev_key.txt", encoding="utf-8").read().strip()

STATE = "他在北京立方庭参观自然语义科技公司，重点了解了新发布的中文分词工具。"

QUESTIONS = {
    "w_company": {
        "type": "noul",
        "instructions": "如果读者没注意到\u201c自然语义科技公司\u201d，理解本段会受损吗？",
        "criteria": {"true": "删掉后段落主干变模糊", "false": "删掉不影响理解"},
    },
    "w_particle": {
        "type": "noul",
        "instructions": "如果读者没注意到\u201c了\u201d，理解本段会受损吗？",
        "criteria": {"true": "删掉后段落主干变模糊", "false": "删掉不影响理解"},
    },
}

ENDPOINTS = [
    "https://api.typesafe.ai/v1/systemone",
    "https://jevmodel.net/v1/systemone",
]

body = json.dumps(
    {"model": "jev-latest", "state": STATE, "questions": QUESTIONS},
    ensure_ascii=False,
).encode("utf-8")

for ep in ENDPOINTS:
    try:
        req = urllib.request.Request(
            ep,
            data=body,
            headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
        )
        t = time.time()
        resp = urllib.request.urlopen(req, timeout=60)
        raw = resp.read().decode("utf-8")
        print("OK", ep, resp.status, "elapsed_ms=", int((time.time() - t) * 1000))
        print(raw[:2000])
        break
    except Exception as e:  # noqa: BLE001
        print("FAIL", ep, str(e)[:300])
