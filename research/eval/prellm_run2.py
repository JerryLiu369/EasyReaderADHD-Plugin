"""前LLM探针 v2：按“关键词所在段落”绑定标签，而非按段序。全走缓存。"""
import json
import re

import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
allparas = []
for cid in ["blog_4701280b0102ec39", "blog_4701280b0102egl0"]:
    art = next(c for c in corpus if c["id"] == cid)
    for p in art["paras"]:
        allparas.append({"cid": cid, "text": p})

labels = json.load(open("eval/prellm_labels.json", encoding="utf-8"))
ranks, hits, keys = [], 0, 0
for lab in labels:
    anchor = lab["keys"][0]
    # 锚定段落：第一个含锚词的段
    idx = next((i for i, p in enumerate(allparas) if anchor in p["text"]), None)
    if idx is None:
        print(f"{lab['job']}: anchor {anchor!r} not found in any para")
        continue
    para = allparas[idx]
    text = para["text"]
    segs = mvp.segment_all([text])[0]
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    score_of = mvp.score_terms(text, uniq)
    ranked = sorted(score_of.items(), key=lambda r: -r[1])
    rank_of = {t: i + 1 for i, (t, _) in enumerate(ranked)}
    exists = [k for k in lab["keys"] if k in text]
    absent = [k for k in lab["keys"] if k not in text]
    print(f"{lab['job']} para#{idx} ({para['cid'][-8:]}) keys_in_para={len(exists)} absent={absent}")
    for k in exists:
        cands = [t for t in rank_of if t == k or k in t or t in k]
        if not cands:
            print(f"   MISS(no cand) {k!r}")
            ranks.append(None)
            continue
        best = max(cands, key=lambda t: score_of[t])
        r = rank_of[best]
        ranks.append(r)
        hits += r <= 3
        keys += 1
        print(f"   rank={r:3d} jev={score_of[best]:.2f} {k!r} -> {best!r}")
rr = [r for r in ranks if r]
print(f"== v2 top-3 hit: {hits}/{keys} = {hits/keys:.3f} | mean rank={sum(rr)/len(rr):.1f} ==")
