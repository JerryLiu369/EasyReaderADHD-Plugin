"""修复：确认 corpus 里两款 blog 都在。春萍若缺，从 sina_sample.html 重新提取。"""
import json
import re

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
ids = {c["id"] for c in corpus}
print("current blog ids:", [c["id"] for c in corpus if c["source"] == "sina-blog"])

if "blog_4701280b0102ec39" not in ids:
    h = open("eval/corpus/raw/sina_sample.html", encoding="utf-8").read()
    m = re.search(r'id="sina_keyword_ad_area2"[^>]*>(.*?)</div>\s*<!--', h, re.S)
    body = m.group(1) if m else ""

    def strip(s):
        s = re.sub(r"<[^>]+>", "", s)
        s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        return re.sub(r"\s+", " ", s).strip()

    paras = [p for p in (strip(c) for c in re.split(r"</?[Dd][Ii][Vv][^>]*>|<br\s*/?>", body))
             if p and len(p) >= 80 and "新浪BLOG反馈" not in p and "About Sina" not in p]
    corpus.append({"source": "sina-blog", "id": "blog_4701280b0102ec39",
                   "title": "韩寒《春萍，我做到了》(2012-11)",
                   "url": "http://blog.sina.com.cn/s/blog_4701280b0102ec39.html",
                   "paras": paras, "era": "preLLM"})
    json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("restored 春萍:", len(paras))
print("blog articles now:",
      [(c["id"][-8:], len(c["paras"])) for c in corpus if c["source"] == "sina-blog"])
