"""端到端 E1：完整管线（候选+打分+渲染）vs E1 人标，看规则栈有没有误杀好词。
走 score_terms（进缓存，可复用）。
"""
import json
import sys

sys.path.insert(0, "eval")
import mvp

e1 = json.load(open("eval/corpus/e1_set.json", encoding="utf-8"))
labels = json.load(open("eval/corpus/e1_labels.json", encoding="utf-8"))

tot_hit, tot_key, misses = 0, 0, []
for i, (para, lab) in enumerate(zip(e1, labels)):
    text = para["text"]
    segs = mvp.segment_all([text])[0]
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    score_of = mvp.score_terms(text, uniq)
    scores = [(s, e, t, score_of[t]) for (s, e, t) in cand]
    html, npick, cov = mvp.render_para(text, scores)
    import re

    picked = re.findall(r"<strong>(.*?)</strong>", html)
    hit = 0
    for k in lab["keys"]:
        # 命中：key 与任一 picked span 互含（子串任一方向）
        ok = any(k in p or p in k for p in picked)
        hit += ok
        if not ok:
            # 诊断：是没进候选，还是分低，还是被抑制？
            cands = [t for t in uniq if t == k or k in t or t in k]
            if not cands:
                why = "no-cand"
            else:
                best = max(cands, key=lambda t: score_of[t])
                why = f"scored {score_of[best]:.2f} as {best!r}"
            misses.append((i, k, why))
    tot_hit += hit
    tot_key += len(lab["keys"])
    print(f"E1-{i:02d} keys hit {hit}/{len(lab['keys'])} spans={npick} cov={cov:.0%}")

print(f"== E2E key coverage: {tot_hit}/{tot_key} = {tot_hit/tot_key:.3f} ==")
from collections import Counter

print(Counter(w for _, _, w in misses).most_common())
for i, k, w in misses:
    print(f"  E1-{i:02d} {k!r}: {w}")
