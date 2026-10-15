"""诊断截图段落：复跑 render 流程，标注每个 picked span 来自 greedy 还是 anchor。"""
import json
import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
art = [c for c in corpus if c["source"] == "jiemian"][0]
para = [p for p in art["paras"] if "潜规则" in p][0]
print("PARA:", para[:200], "... len=", len(para))

segs = mvp.segment_all([para])[0]
cand = mvp.build_candidates(para, segs)
seen, uniq = {}, []
for (_, _, t) in cand:
    if t not in seen:
        seen[t] = True
        uniq.append(t)
scores = [(s, e, t, mvp.score_terms(para, uniq)[t]) for (s, e, t) in cand]

# 复刻 greedy，打印每词决策
total = sum(1 for ch in para if ch not in mvp.PUNCT) or 1
tscore = {t: n for (s, e, t, n) in scores for t in [t]}
ranked = sorted(tscore, key=lambda t: -tscore[t])
print("top 25 terms:")
for t in ranked[:25]:
    occ = sum(1 for r in scores if r[2] == t)
    print(f"  {tscore[t]:.2f} x{occ} {t!r}")
