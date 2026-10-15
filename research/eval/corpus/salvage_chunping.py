import json
import re

h = open("eval/corpus/raw/sina_sample.html", encoding="utf-8").read()
m = re.search(r'id="sina_keyword_ad_area2"[^>]*>(.*?)</div>\s*<!--', h, re.S)
print("has body:", bool(m))
print("len:", len(h))


def strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


body = m.group(1) if m else ""
chunks = re.split(r"</?[Dd][Ii][Vv][^>]*>|<br\s*/?>", body)
out = []
for p in (strip(c) for c in chunks):
    if p and len(p) >= 80 and "新浪BLOG意见反馈" not in p and "About Sina" not in p:
        out.append(p)
print("paras:", len(out))
for p in out[:3]:
    print("  ", p[:70])
