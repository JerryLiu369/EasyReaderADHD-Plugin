"""E1：20 段 × 1 请求/段，批量 noul（英文 wording），输出排名指标。
预算：eval/.usage.json 计数，100 次封顶（含 E0 已用的 2 次）。
"""
import json
import time
import urllib.request
import urllib.error

EP = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
USAGE_FILE = "eval/.usage.json"
BUDGET = 100


def usage():
    try:
        return json.load(open(USAGE_FILE, encoding="utf-8"))
    except FileNotFoundError:
        return {"requests": 0, "input_tokens": 0, "output_tokens": 0}


def save_usage(u):
    json.dump(u, open(USAGE_FILE, "w", encoding="utf-8"), indent=1)


def mk_q(term):
    return {
        "type": "noul",
        "instructions": {
            "target": term,
            "question": "Would a reader missing `target` fail to grasp this paragraph's main point?",
        },
        "criteria": {
            "true": "Removing it blurs who, what, where, or the key event or claim",
            "false": "A function word, filler, or detail whose removal changes nothing",
        },
    }


def call(state, questions):
    u = usage()
    if u["requests"] >= BUDGET:
        raise RuntimeError(f"budget exhausted: {u['requests']}/{BUDGET}")
    body = json.dumps(
        {"model": MODEL, "state": state, "questions": questions}, ensure_ascii=False
    ).encode("utf-8")
    key = open("jev_key.txt", encoding="utf-8").read().strip()
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                EP,
                data=body,
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            )
            t = time.time()
            resp = urllib.request.urlopen(req, timeout=90)
            raw = json.loads(resp.read().decode("utf-8"))
            u["requests"] += 1
            u["input_tokens"] += raw.get("usage", {}).get("input_tokens", 0)
            u["output_tokens"] += raw.get("usage", {}).get("output_tokens", 0)
            save_usage(u)
            return raw, int((time.time() - t) * 1000)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (429, 529):
                time.sleep(2**attempt * 2)
                continue
            raise
    raise last


if __name__ == "__main__":
    e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
    labels = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
    results = []
    for i, (para, lab) in enumerate(zip(e1, labels)):
        terms = [(t, 1) for t in lab["keys"]] + [(t, 0) for t in lab["distractors"]]
        qs = {f"q{j}": mk_q(t) for j, (t, _) in enumerate(terms)}
        raw, ms = call(para["text"], qs)
        scored = [
            {"term": t, "label": lb, "noul": raw["answers"][f"q{j}"]["noul"]}
            for j, (t, lb) in enumerate(terms)
        ]
        scored.sort(key=lambda r: -r["noul"])
        nk = len(lab["keys"])
        topk = scored[:nk]
        p_at_k = sum(r["label"] for r in topk) / nk
        p_at_3 = sum(r["label"] for r in scored[:3]) / 3
        # 虚词误伤：distractor 里的是单字虚词，进 top-30% 的比例
        particles = [r for r in scored if r["label"] == 0 and len(r["term"]) == 1]
        top30 = scored[: max(1, int(len(scored) * 0.3))]
        false_hit = (
            sum(1 for r in top30 if r in particles) / len(particles) if particles else 0
        )
        mean_key = sum(r["noul"] for r in scored if r["label"]) / nk
        mean_dis = sum(r["noul"] for r in scored if not r["label"]) / (len(scored) - nk)
        results.append(
            {
                "id": i,
                "ms": ms,
                "usage": raw.get("usage"),
                "p_at_k": round(p_at_k, 3),
                "p_at_3": round(p_at_3, 3),
                "false_hit": round(false_hit, 3),
                "mean_key": round(mean_key, 3),
                "mean_dis": round(mean_dis, 3),
                "ranking": [(r["term"], r["noul"], r["label"]) for r in scored],
            }
        )
        print(
            f"E1-{i:02d} ms={ms} P@K={p_at_k:.2f} P@3={p_at_3:.2f} "
            f"key={mean_key:.2f} dis={mean_dis:.2f} toks={raw.get('usage')}"
        )
    json.dump(results, open("eval/e1_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = len(results)
    print("---- MEAN ----")
    for m in ["p_at_k", "p_at_3", "false_hit", "mean_key", "mean_dis"]:
        print(m, round(sum(r[m] for r in results) / n, 3))
    print("usage:", usage())
