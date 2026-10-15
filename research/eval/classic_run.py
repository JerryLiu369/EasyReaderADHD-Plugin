"""前 AI 时代泛化探针：鲁迅/老舍/史记 17 段，打分 + 对齐 + 独立渲染页。"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp


def load_txt(path):
    return [x.strip() for x in open(path, encoding="utf-8").read().split("\n\n") if x.strip()]


jobs = []
for fid, pre, title, url in [
    ("nalai", "N", "鲁迅《拿来主义》(1934)", "https://zh.wikisource.org/wiki/拿来主义"),
    ("jinan", "J", "老舍《济南的冬天》(1931)", "https://zh.wikibooks.org/wiki/初中语文/七年级上册/济南的冬天（老舍）"),
    ("xiangyu", "X", "《史记·项羽本纪》乌江段", "https://zh.wikisource.org/wiki/史記/卷007"),
]:
    for k, p in enumerate(load_txt(f"eval/corpus/raw/{fid}.txt")):
        jobs.append({"job": f"{pre}{k}", "title": title, "url": url, "text": p})

mine = {m["job"]: m["keys"] for m in json.load(open("eval/classic_labels.json", encoding="utf-8"))}
assert {j["job"] for j in jobs} == set(mine), "jobs/labels mismatch"

sections, ranks_all, hit_all, key_all = [], [], 0, 0
for j in jobs:
    text = j["text"]
    segs = mvp.segment_all([text])[0]
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    score_of = mvp.score_terms(text, uniq)
    scores = [(s, e, t, score_of[t]) for (s, e, t) in cand]
    ranked = sorted(score_of.items(), key=lambda r: -r[1])
    rank_of = {t: i + 1 for i, (t, _) in enumerate(ranked)}
    print(f"===== {j['job']} len={len(text)} cand={len(uniq)} =====")
    for k in mine[j["job"]]:
        cands = [t for t in rank_of if t == k or k in t or t in k]
        if not cands:
            print(f"  MISS(no cand) {k!r}")
            ranks_all.append(None)
            continue
        best = max(cands, key=lambda t: score_of[t])
        r = rank_of[best]
        ranks_all.append(r)
        hit_all += r <= max(3, len(mine[j["job"]]))
        key_all += 1
        print(f"  rank={r:3d} jev={score_of[best]:.2f} {k!r} -> {best!r}")
    html, npick, cov = mvp.render_para(text, scores)
    print(f"  picked {npick} cov={cov:.0%}")
    sections.append(f"<h1>{j['title']} · {j['job']}</h1><p>{html}</p>")

rr = [r for r in ranks_all if r]
print(f"== CLASSIC mean rank={sum(rr)/len(rr):.1f} hit@{len(mine)}={hit_all}/{key_all} = {hit_all/key_all:.3f} ==")

doc = ("<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
       "<style>body{max-width:34em;margin:3em auto;line-height:2;font-size:18px;"
       "font-family:system-ui,'PingFang SC','Microsoft YaHei',serif}"
       "strong{font-weight:700;padding:0 .08em}h1{font-size:20px;margin-top:2.5em}</style></head><body>"
       "<div style='background:#eef;border:1px solid #99c;padding:8px 12px;font-size:14px'>前AI探针 · 鲁迅/老舍/史记</div>"
       + "".join(sections) + "</body></html>")
open("eval/mvp_classic.html", "w", encoding="utf-8").write(doc)
print("wrote eval/mvp_classic.html")
