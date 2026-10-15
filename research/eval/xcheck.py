"""互证：同一20段holdout，Jev管线 vs LLM二评（盲）。
指标：P@K(K=LLM keys数，模糊匹配）+ E2E渲染覆盖 + mean rank + junk率。输出HTML供人眼。
Jev请求约20-30个，走缓存记账。"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

hold = json.load(open("eval/holdout.json", encoding="utf-8"))["paras"]
labs = json.load(open("eval/llm_labels.json", encoding="utf-8"))


def match(key, term):
    k = key.replace(" ", "").replace("　", "")
    t = term.replace(" ", "").replace("　", "")
    return k == t or k in t or t in k


pks, ranks_all, cov_h, cov_t = [], [], 0, 0
junks, sections, details = [], [], []
for lab, p in zip(labs, hold):
    assert lab["text"] == p["text"], f"text mismatch {lab['i']}"
    text, keys = p["text"], lab["keys"]
    segs = mvp.segment_all([text])[0]
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    score_of = mvp.score_terms(text, uniq)
    ranked = sorted(score_of.items(), key=lambda r: -r[1])
    rank_of = {t: i + 1 for i, (t, _) in enumerate(ranked)}
    K = len(keys)
    topk = [t for (t, _) in ranked[:K]]
    hits = sum(1 for k in keys if any(match(k, t) for t in topk))
    pks.append(hits / K if K else 0)
    for k in keys:
        rs = [rank_of[t] for t in rank_of if match(k, t)]
        ranks_all.append(min(rs) if rs else None)
    html, npick, cov = mvp.render_para(
        text, [(s, e, t, score_of[t]) for (s, e, t) in cand])
    picked = re.findall(r"<strong>(.*?)</strong>", html)
    cov_h += sum(1 for k in keys if any(match(k, s) for s in picked))
    cov_t += K
    junks.extend([s for s in picked if s in mvp.STOP])
    miss = [k for k in keys if not any(match(k, s) for s in picked)]
    details.append({"i": lab["i"], "doc": p["doc"], "K": K, "pk": round(hits / max(1, K), 2),
                    "picked": picked, "miss": miss})
    print(f"{lab['i']:02d} doc={p['doc'][-8:]} K={K} P@K={hits/max(1,K):.2f} miss={miss} | picked={picked}")
    sections.append(f"<h1>#{lab['i']:02d} {p['doc'][-12:]}（LLM标{K}个，P@K={hits/max(1,K):.2f}）</h1>"
                    f"<p>{html}</p><p class='llm'>LLM keys：{' / '.join(keys)}</p>")

rr = [r for r in ranks_all if r]
print(f"== HOLDOUT P@K={sum(pks)/len(pks):.3f} E2Ecov={cov_h}/{cov_t}={cov_h/cov_t:.3f} "
      f"meanrank={sum(rr)/len(rr):.1f} nonecand={ranks_all.count(None)} junk={junks} reqs={mvp.usage()['requests']} ==")
json.dump(details, open("eval/holdout_xcheck.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
doc = ("<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
       "<style>body{max-width:34em;margin:3em auto;line-height:2;font-size:18px;"
       "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif}"
       "strong{font-weight:700;padding:0 .08em}h1{font-size:18px;margin-top:2em}"
       ".llm{font-size:13px;color:#666;background:#f6f6f6;padding:6px 10px}</style></head><body>"
       "<div style='background:#efe;border:1px solid #9c9;padding:8px 12px;font-size:14px'>"
       "Holdout互证 · 全新语料（sspai 114869/115237 + 观察者时政）· Jev管线零调整 vs LLM盲标</div>"
       + "".join(sections) + "</body></html>")
open("eval/mvp_holdout.html", "w", encoding="utf-8").write(doc)
print("wrote eval/mvp_holdout.html eval/holdout_xcheck.json")
