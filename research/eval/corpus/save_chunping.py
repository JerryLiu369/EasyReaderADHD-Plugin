"""入库已救回的前 LLM 语料：韩寒《春萍》14 段（2012-11）。"""
import json
import re

h = open("eval/corpus/raw/sina_sample.html", encoding="utf-8").read()
m = re.search(r'id="sina_keyword_ad_area2"[^>]*>(.*?)</div>\s*<!--', h, re.S)
body = m.group(1) if m else ""


def strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


paras = []
for p in (strip(c) for c in re.split(r"</?[Dd][Ii][Vv][^>]*>|<br\s*/?>", body)):
    if p and len(p) >= 80 and "新浪BLOG意见反馈" not in p and "About Sina" not in p:
        paras.append(p)

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
corpus = [c for c in corpus if c["id"] != "blog_4701280b0102ec39"]
corpus.append({"source": "sina-blog", "id": "blog_4701280b0102ec39",
               "title": "韩寒《春萍，我做到了》(2012-11)",
               "url": "http://blog.sina.com.cn/s/blog_4701280b0102ec39.html",
               "paras": paras, "era": "preLLM"})
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved paras:", len(paras), "| articles:", len(corpus))
