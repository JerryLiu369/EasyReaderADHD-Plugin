"""扩 corpus：观察者时政 ×1、界面财经 ×1、豆瓣书评 ×1。追加进 corpus.json。"""
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
    return re.sub(r"\s+", " ", s).strip()


def title_of(h):
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    return strip(m.group(1))[:60] if m else "?"


def keep(ps):
    return [p for p in (strip(p) for p in ps) if 80 <= len(p) <= 600]


# 1. 观察者政事
h = get("https://www.guancha.cn/")
zz = sorted(set(re.findall(r'href="(/ZhengZhi/[^"]*?\.shtml)"', h)))
art = None
for link in zz[:8]:
    try:
        g = get("https://www.guancha.cn" + link)
        i = g.find("all-txt")
        seg = g[i : i + 300000]
        ps = keep(re.findall(r"<p>(.*?)</p>", seg, re.S))
        t = title_of(g)
        print("guancha", link, len(ps), t)
        if len(ps) >= 8:
            art = ("guancha", link, t, "https://www.guancha.cn" + link, ps)
            break
    except Exception as e:  # noqa: BLE001
        print("FAIL guancha", link, str(e)[:120])

# 2. 界面财经（已验证 13163796）
j = get("https://www.jiemian.com/article/13163796.html")
i = j.find("article-content")
ps = keep(re.findall(r"<p[^>]*>(.*?)</p>", j[i : i + 200000], re.S))
t = title_of(j)
print("jiemian", len(ps), t)
art2 = ("jiemian", "13163796", t, "https://www.jiemian.com/article/13163796.html", ps)

# 3. 豆瓣书评
r = get("https://book.douban.com/review/17852978/")
i = r.find("review-content")
ps = keep(re.findall(r"<p[^>]*>(.*?)</p>", r[i : i + 100000], re.S))
t = title_of(r)
print("douban", len(ps), t)
art3 = ("douban", "17852978", t, "https://book.douban.com/review/17852978/", ps)

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
for s, i_, t, url, ps in [a for a in [art, art2, art3] if a]:
    corpus.append({"source": s, "id": i_, "title": t, "url": url, "paras": ps})
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total articles:", len(corpus))
