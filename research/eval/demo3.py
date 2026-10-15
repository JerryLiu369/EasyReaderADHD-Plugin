"""三篇演示页：跑后拉伸 + 大国竞争 + 韩寒春萍，v10 管线。输出 eval/demo3.html。"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}

JOBS = ["115568", "cssn-2022", "blog_4701280b0102ec39"]
sections = []
for cid in JOBS:
    c = by_id[cid]
    paras = [p for p in c["paras"] if sum(1 for ch in p if "\u4e00" <= ch <= "\u9fff") >= 15]
    print(f"=== {c['title'][:30]} n={len(paras)} ===")
    rendered = []
    seg_lists = mvp.segment_all(paras)
    for text, seg_list in zip(paras, seg_lists):
        cand = mvp.build_candidates(text, seg_list)
        seen, uniq = {}, []
        for (_, _, t) in cand:
            if t not in seen:
                seen[t] = True
                uniq.append(t)
        score_of = mvp.score_terms(text, uniq)
        html, npick, cov = mvp.render_para(
            text, [(s, e, t, score_of[t]) for (s, e, t) in cand])
        rendered.append(html)
    inner = "".join(f"<p>{p}</p>" for p in rendered)
    sections.append(
        f"<h1>{c['title'][:45]}</h1>"
        f"<p class='src'><a href='{c['url']}'>{c['url']}</a>（{len(paras)} 段）</p>" + inner)

doc = ("<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
       "<style>body{max-width:34em;margin:3em auto;line-height:2;font-size:18px;"
       "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif}"
       "strong{font-weight:700;padding:0 .08em}h1{font-size:22px;margin-top:2.5em;"
       "border-top:3px solid #333;padding-top:1em}.src{font-size:13px;color:#888}</style></head><body>"
       "<div style='background:#eef;border:1px solid #99c;padding:8px 12px;font-size:14px;color:#333'>"
       "v14 三篇演示 · 跑后拉伸 / 大国竞争的根源 / 韩寒《春萍，我做到了》</div>"
       + "".join(sections) + "</body></html>")
open("eval/demo3.html", "w", encoding="utf-8").write(doc)
print("wrote eval/demo3.html requests:", mvp.usage()["requests"])
