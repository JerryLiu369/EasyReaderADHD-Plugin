import json
import re

c = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
a = [x for x in c if x["id"] == "17852957"][0]
print("n=", len(a["paras"]))


def cjk(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


pat = re.compile(r"[{();=']")


def is_code(p):
    return bool(pat.search(p)) and cjk(p) < 20


for p in a["paras"][:14]:
    print(len(p), cjk(p), "CODE" if is_code(p) else "ok", repr(p[:55]))
