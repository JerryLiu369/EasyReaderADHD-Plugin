"""前LLM探针：韩寒 2012《春萍》14 段 + 2013《地震思考录》8 段，同一 v3 管线。"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
chunping = next(c for c in corpus if c["id"] == "blog_4701280b0102ec39")
quake = next(c for c in corpus if c["id"] == "blog_4701280b0102egl0")

JOBS = []
for k, p in enumerate(chunping["paras"]):
    JOBS.append({"job": f"H{k}", "title": "春萍", "text": p})
for k, p in enumerate(quake["paras"]):
    JOBS.append({"job": f"H{14 + k}", "title": "地震", "text": p})

labels = {m["job"]: m["keys"] for m in json.load(open("eval/prellm_labels.json", encoding="utf-8"))}
sections, ranks, hits, keys = [], [], 0, 0
for j in JOBS:
    text = j["text"]
    segs = mvp.segment_all([text])[0]
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    score_of = mvp.score_terms(text, uniq)
    scores = [(s, e, t, score_of[t]) for (s, e, t) in cand]
    ranked = sorted(score_of.items(), key=lambda r: -r[1])
    rank_of = {t: i + 1 for i, (t, _) in enumerate(ranked)}
    mykeys = labels.get(j["job"], [])
    print(f"===== {j['job']} ({j['title']}) len={len(text)} cand={len(uniq)} =====")
    for k in mykeys:
        cands = [t for t in rank_of if t == k or k in t or t in k]
        if not cands:
            print(f"  MISS(no cand) {k!r}")
            ranks.append(None)
            continue
        best = max(cands, key=lambda t: score_of[t])
        r = rank_of[best]
        ranks.append(r)
        ok = r <= max(3, len(mykeys))
        hits += ok
        keys += 1
        print(f"  rank={r:3d} jev={score_of[best]:.2f} {k!r} -> {best!r}")
    html, npick, cov = mvp.render_para(text, scores)
    print(f"  picked {npick} cov={cov:.0%}")
    sections.append(f"<h1>韩寒《{j['title']}》· {j['job']}</h1><p>{html}</p>")

rr = [r for r in ranks if r]
print(f"== PRE-LLM mean rank={sum(rr)/len(rr):.1f} hit={hits}/{keys}={hits/keys:.3f} ==")
doc = ("<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
       "<style>body{max-width:34em;margin:3em auto;line-height:2;font-size:18px;"
       "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif}"
       "strong{font-weight:700;padding:0 .08em}h1{font-size:20px;margin-top:2.5em}</style></head><body>"
       "<div style='background:#ffe;border:1px solid #cc9;padding:8px 12px;font-size:14px'>"
       "前大模型探针 · 韩寒博客 2012/2013 · 同一 v3 管线零调整</div>"
       + "".join(sections) + "</body></html>")
open("eval/mvp_prellm.html", "w", encoding="utf-8").write(doc)
print("wrote eval/mvp_prellm.html")
