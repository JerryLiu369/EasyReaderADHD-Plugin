"""两图复现：韩寒密度不均段 + cssn 地缘竞争段。落盘 dbg_density.txt。"""
import io
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}
hp = next(p for p in by_id["blog_4701280b0102ec39"]["paras"] if "黯然抑郁" in p)
cp = next(p for p in by_id["cssn-2022"]["paras"] if "最古老的一种大国竞争" in p)

out = io.StringIO()
for name, text in [("HANHAN", hp), ("CSSN", cp)]:
    out.write(f"===== {name} len={len(text)}\n{text}\n")
    segs = mvp.segment_all([text])[0]
    out.write(f"SEGS: {[s['text'] for s in segs]}\n")
    cand = mvp.build_candidates(text, segs)
    uniq = sorted({t for (_, _, t) in cand})
    sc = mvp.score_terms(text, uniq)
    ranked = sorted(sc.items(), key=lambda r: -r[1])
    out.write(f"cand_n={len(uniq)}\n")
    for t, s in ranked[:20]:
        out.write(f"  {s:.2f} {t}\n")
    html, npick, cov = mvp.render_para(
        text, [(s, e, t, sc[t]) for (s, e, t) in cand])
    out.write(f"rendered_cov={cov:.0%} picks={re.findall(r'<strong>(.*?)</strong>', html)}\n")
    # 按子句看分布
    for s0, sent in mvp.split_sentences(text):
        s1 = s0 + len(sent)
        in_cl = [t for (s, e, t) in cand if s0 <= s and e <= s1]
        picked_in = [m for m in re.findall(r"<strong>(.*?)</strong>", html)
                     if m in text[s0:s1]]
        out.write(f"  clause[{text[s0:s0+18]}…] clen={mvp.content_len(sent)} picks={picked_in}\n")
open("eval/dbg_density.txt", "w", encoding="utf-8").write(out.getvalue())
print("wrote eval/dbg_density.txt")
