import sys

sys.path.insert(0, "eval")
import mvp
import json

cache = mvp.load_cache()
corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
jm = [c for c in corpus if c["source"] == "jiemian"][0]
para = [p for p in jm["paras"] if "异地代缴" in p][0]
segs = mvp.segment_all([para])[0]
cand = mvp.build_candidates(para, segs)
uniq = sorted({t for (_, _, t) in cand})
scored = sorted(
    [(t, cache.get(mvp.cache_key(para, t))) for t in uniq], key=lambda r: -(r[1] or -1)
)
print("top 20:")
for t, s in scored[:20]:
    print(f"  {s} {t!r}")
print("异地代缴 rank:", next(i for i, (t, _) in enumerate(scored, 1) if t == "异地代缴"))

gc = [c for c in corpus if c["source"] == "guancha"][0]
p2 = [p for p in gc["paras"] if "黄精五黑粉" in p][0]
h = open("eval/mvp_multi.html", encoding="utf-8").read()
i = h.find("黄精五黑粉")
import re
print(repr(h[max(0, i - 60) : i + 60]))
