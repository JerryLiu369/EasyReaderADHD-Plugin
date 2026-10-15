import sys

sys.path.insert(0, "eval")
import mvp

cache = mvp.load_cache()
corpus = __import__("json").load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}

for cid, needle, terms in [
    ("13163796", "异地代缴", ["异地代缴", "异地代", "异地", "代缴"]),
    ("guancha", None, None),
]:
    pass

jm = by_id["13163796"]
para = [p for p in jm["paras"] if "异地代缴" in p][0]
print("PARA:", para[-120:])
for t in ["异地代缴", "异地代", "异地", "代缴", "再如异地代缴"]:
    print(f"  {t!r} =", cache.get(mvp.cache_key(para, t), "MISS"))

gc = [c for c in corpus if c["source"] == "guancha"][0]
para2 = [p for p in gc["paras"] if "黄精五黑粉" in p][0]
print("PARA2:", para2[:100])
for t in ["黄精五黑粉", "五黑粉", "黑粉", "黄精"]:
    print(f"  {t!r} =", cache.get(mvp.cache_key(para2, t), "MISS"))
