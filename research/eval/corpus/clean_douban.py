"""豆瓣去码：去掉 review-content 切片带入的页面脚本/元数据行。"""
import json
import re

pat = re.compile(r"[{();=']")


def cjk(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def is_junk(p):
    if any(b in p for b in ("FRODO", "api/v2", "data-url", "http", "&copy")):
        return True
    return bool(pat.search(p)) and cjk(p) < 20


f = open("eval/corpus/corpus.json", encoding="utf-8")
c = json.load(f)
f.close()
for a in c:
    if a["source"] != "douban":
        continue
    n0 = len(a["paras"])
    a["paras"] = [p for p in a["paras"] if not is_junk(p)]
    print(a["id"], n0, "->", len(a["paras"]))
f = open("eval/corpus/corpus.json", "w", encoding="utf-8")
json.dump(c, f, ensure_ascii=False, indent=1)
f.close()
print("saved")
