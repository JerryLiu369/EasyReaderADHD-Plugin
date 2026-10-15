"""抓 3 篇前大模型博客正文：韩寒 2012×2 + 和菜头 2006。"""
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = re.sub(r"\s+", " ", s).strip()
    return s


jobs = [
    ("twocold", "blog_4701280b0102eb6w.html", "韩寒《ONE IS ALL》(2012-10)"),
    ("twocold", "blog_4701280b0102ec39.html", "韩寒《春萍，我做到了》(2012-11)"),
    ("hecaitou", "blog_53f02cd2010003t1.html", "和菜头《ZION》(2006-03)"),
]
corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
for author, pid, title in jobs:
    h = get(f"http://blog.sina.com.cn/s/{pid}")
    m = re.search(r'id="sina_keyword_ad_area2"(.*)', h, re.S)
    body = m.group(1)[:200000] if m else h
    body = re.sub(r"^[^>]*>", "", body)  # 去 opening div 残留
    paras = [strip(p) for p in re.split(r"</?[Dd][Ii][Vv][^>]*>", body)]
    paras = [p for p in paras
             if 80 <= len(p) <= 600 and "新浪BLOG意见反馈" not in p and "About Sina" not in p]
    print(title, "paras:", len(paras))
    for p in paras[:3]:
        print("   ", p[:80])
    corpus.append({"source": "sina-blog", "id": pid, "title": title,
                   "url": f"http://blog.sina.com.cn/s/{pid}", "paras": paras,
                   "era": "preLLM"})
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("articles:", len(corpus))
