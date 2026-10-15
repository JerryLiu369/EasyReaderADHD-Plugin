import json
import re

h = open("eval/corpus/raw/thepaper_sample.html", encoding="utf-8").read()
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', h, re.S)
print("json len:", len(m.group(1)) if m else 0)
d = json.loads(m.group(1))
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        if o and isinstance(o[0], str) and len("".join(o)) > 500:
            print(path, "str-list total len:", len("".join(o)))
        for i, v in enumerate(o[:3]):
            walk(v, path + f"[{i}]")
    elif isinstance(o, str) and len(o) > 800:
        print(path, "len:", len(o), repr(o[:120]))
walk(d)
