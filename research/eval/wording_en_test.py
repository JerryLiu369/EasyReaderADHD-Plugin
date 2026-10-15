"""对照组：同一中文 state，英文 wording，看分离度是否更好。"""
import json
import time
import urllib.request

KEY = open("jev_key.txt", encoding="utf-8").read().strip()
EP = "https://api.typesafe.ai/v1/systemone"

STATE = "他在北京立方庭参观自然语义科技公司，重点了解了新发布的中文分词工具。"

def mk_q(term):
    return {
        "type": "noul",
        "instructions": {
            "target": term,
            "question": "Would a reader missing `target` fail to grasp this paragraph's main point?",
        },
        "criteria": {
            "true": "Removing it blurs who, where, or the key event",
            "false": "A function word or detail whose removal changes nothing",
        },
    }


QUESTIONS = {"w_company": mk_q("自然语义科技公司"), "w_particle": mk_q("了")}
# state 保持纯段落字符串：判断所需的全部上下文就是段落本身
BODY_STATE = STATE

body = json.dumps(
    {"model": "jev-latest", "state": BODY_STATE, "questions": QUESTIONS},
    ensure_ascii=False,
).encode("utf-8")

req = urllib.request.Request(
    EP, data=body, headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
)
t = time.time()
try:
    resp = urllib.request.urlopen(req, timeout=60)
    raw = resp.read().decode("utf-8")
    print("OK", resp.status, "elapsed_ms=", int((time.time() - t) * 1000))
    print(raw[:2000])
except Exception as e:  # noqa: BLE001
    print("FAIL", str(e)[:500])
