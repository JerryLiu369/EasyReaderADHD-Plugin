"""核实评审指控：V1 界面内部重复；V2 观察者编号跳跃；V3 离心收缩得分。"""
import json
from collections import Counter

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))

# V1
jm = [c for c in corpus if c["source"] == "jiemian"][0]
print("jiemian paras:", len(jm["paras"]))
seen = {}
for i, p in enumerate(jm["paras"]):
    seen.setdefault(p[:60], []).append(i)
for k, v in seen.items():
    if len(v) > 1:
        print("  DUP:", v, k[:50])

# V2
gc = [c for c in corpus if c["source"] == "guancha"][0]
for i, p in enumerate(gc["paras"]):
    if "第一" in p[:20] or "第二" in p[:20] or "第三" in p[:20]:
        print(f"  guancha-{i}:", p[:60])

# V3
cache = json.load(open("eval/.score_cache.json", encoding="utf-8"))
import hashlib


def key(state, term):
    return hashlib.sha1(f"en-v1|{state}|{term}".encode("utf-8")).hexdigest()[:20]


ssp = [c for c in corpus if c["id"] == "115568"][0]
for i, p in enumerate(ssp["paras"]):
    if "离心收缩" in p:
        for t in ["离心收缩", "离心", "收缩", "刹住", "刹住身体", "大腿", "腿"]:
            print(f"  para{i} {t!r} =", cache.get(key(p, t), "MISS"))
