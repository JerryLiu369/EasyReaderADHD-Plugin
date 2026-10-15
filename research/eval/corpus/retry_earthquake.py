import json
import re
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "Referer": "http://blog.sina.com.cn/twocold"}


def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


def extract(h):
    m = re.search(r'id="sina_keyword_ad_area2"[^>]*>(.*?)</div>\s*<!--', h, re.S)
    body = m.group(1) if m else ""
    out = []
    for p in (strip(c) for c in re.split(r"</?[Dd][Ii][Vv][^>]*>|<br\s*/?>", body)):
        if p and len(p) >= 80 and "新浪BLOG意见反馈" not in p and "About Sina" not in p:
            out.append(p)
    return out


tries = [
    "http://blog.sina.com.cn/s/blog_4701280b0102egl0.html",
    "https://blog.sina.com.cn/s/blog_4701280b0102egl0.html",
]
h2 = None
for u in tries:
    try:
        h2 = get(u)
        print("OK", u, len(h2))
        break
    except Exception as e:  # noqa: BLE001
        print("FAIL", u, str(e)[:80])
    time.sleep(15)
if h2:
    ps = extract(h2)
    print("地震思考录 paras:", len(ps))
    corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
    corpus = [c for c in corpus if c["id"] != "blog_4701280b0102egl0"]
    if ps:
        corpus.append({"source": "sina-blog", "id": "blog_4701280b0102egl0",
                       "title": "韩寒《地震思考录》(2013-04)",
                       "url": "http://blog.sina.com.cn/s/blog_4701280b0102egl0.html",
                       "paras": ps, "era": "preLLM"})
        json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("articles:", len(corpus))
