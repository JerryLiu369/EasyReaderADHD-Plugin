"""Prompt 调优：同一 3 段 × 同一组词，对比不同问法的质量与 token。
A=现状（基线，走 e1_results.json，0 新请求）
B=短问句（单字符串，无 criteria）
C=单 choice 题（全部候选当 option，按 probabilities 排名）
D=50 题/批接受度（只看接口与分数 sanity）
"""
import json
import sys

sys.path.insert(0, "eval")
from mvp import call_jev

E1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
LAB = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))
PICK = [2, 7, 15]  # Ollama / 索尼奔腾 / 审判萨达姆


def terms_of(i):
    lab = LAB[i]
    return [(t, 1) for t in lab["keys"]] + [(t, 0) for t in lab["distractors"]]


def report(name, i, ranked, usage):
    # ranked: [(term, label, score)] 已按分降序
    nk = sum(1 for _, lb in terms_of(i) if lb)
    topk = ranked[:nk]
    p_at_k = sum(lb for _, lb, _ in topk) / nk
    p_at_3 = sum(lb for _, lb, _ in ranked[:3]) / 3
    mk = sum(s for _, lb, s in ranked if lb) / nk
    md = sum(s for _, lb, s in ranked if not lb) / (len(ranked) - nk)
    it = usage.get("input_tokens", 0)
    print(f"{name} E1-{i:02d} P@K={p_at_k:.2f} P@3={p_at_3:.2f} key={mk:.2f} dis={md:.2f} in_tok={it} tok/Q={it/len(ranked):.0f}")
    return {"variant": name, "id": i, "p_at_k": round(p_at_k, 3), "p_at_3": round(p_at_3, 3),
            "mean_key": round(mk, 3), "mean_dis": round(md, 3), "in_tok": it,
            "tok_per_q": round(it / len(ranked), 1)}


results = []
# A 基线
base = {r["id"]: r for r in json.load(open("eval/e1_results.json", encoding="utf-8"))}
for i in PICK:
    r = base[i]
    ranked = [(t, lb, s) for (t, s, lb) in r["ranking"]]
    results.append(report("A-baseline", i, ranked, {"input_tokens": 1200}))

# B 短问句
for i in PICK:
    terms = terms_of(i)
    qs = {f"q{j}": {"type": "noul", "instructions": f"Is {t!r} essential to this paragraph's main point?"}
          for j, (t, _) in enumerate(terms)}
    raw, ms = call_jev(E1[i]["text"], qs)
    ranked = sorted(
        [(t, lb, raw["answers"][f"q{j}"]["noul"]) for j, (t, lb) in enumerate(terms)],
        key=lambda r: -r[2],
    )
    results.append(report("B-short", i, ranked, raw.get("usage", {})))

# C 单 choice
for i in PICK:
    terms = terms_of(i)
    qs = {"rank": {"type": "choice",
                   "instructions": "Which term is most essential to this paragraph's main point?",
                   "criteria": {t: None for (t, _) in terms}}}
    raw, ms = call_jev(E1[i]["text"], qs)
    probs = raw["answers"]["rank"]["probabilities"]
    ranked = sorted([(t, lb, probs[t]) for (t, lb) in terms], key=lambda r: -r[2])
    results.append(report("C-choice", i, ranked, raw.get("usage", {})))

# D 大批量
para = E1[2]["text"]
big_qs = {f"q{j}": {"type": "noul", "instructions": f"Is 'word{j}' essential to this paragraph's main point?"}
          for j in range(50)}
raw, ms = call_jev(para, big_qs)
print(f"D-batch50 ok={len(raw['answers'])==50} ms={ms} toks={raw.get('usage')}")

json.dump(results, open("eval/tune_results.json", "w", encoding="utf-8"), indent=1)
print("---- MEAN (A vs B vs C) ----")
for v in ["A-baseline", "B-short", "C-choice"]:
    rs = [r for r in results if r["variant"] == v]
    print(v, {m: round(sum(r[m] for r in rs) / len(rs), 3) for m in ["p_at_k", "p_at_3", "mean_key", "mean_dis", "tok_per_q"]})
