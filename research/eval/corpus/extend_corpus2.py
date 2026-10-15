"""扩 corpus v2：豆瓣按换行切 stanza；观察者取 15 篇里最长的。先把上次追加的 3 条砍掉重来。"""
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip(s):
    s = re.sub(r"<[^>]+>", "\n", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return s


def keep(ps):
    return [re.sub(r"\s+", " ", p).strip() for p in ps if 80 <= len(re.sub(r"\s+", " ", p).strip()) <= 600]


def title_of(h):
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip()[:60] if m else "?"


corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
corpus = [c for c in corpus if c["source"] == "sspai"]
print("truncated to sspai:", len(corpus))

# 1. 观察者：扫 15 篇取最长
h = get("https://www.guancha.cn/")
zz = sorted(set(re.findall(r'href="(/ZhengZhi/[^"]*?\.shtml)"', h)))[:15]
best = None
for link in zz:
    try:
        g = get("https://www.guancha.cn" + link)
        i = g.find("all-txt")
        if i < 0:
            continue
        ps = keep(re.findall(r"<p>(.*?)</p>", g[i : i + 300000], re.S))
        if not best or len(ps) > len(best[0]):
            best = (ps, link, title_of(g))
        print("guancha", link, len(ps))
    except Exception as e:  # noqa: BLE001
        print("FAIL", link, str(e)[:100])
ps, link, t = best
print("picked:", link, len(ps), t)
corpus.append({"source": "guancha", "id": link, "title": t, "url": "https://www.guancha.cn" + link, "paras": ps})

# 2. 界面（沿用已验证）
j = get("https://www.jiemian.com/article/13163796.html")
i = j.find("article-content")
ps = keep(re.findall(r"<p[^>]*>(.*?)</p>", j[i : i + 200000], re.S))
t = title_of(j)
print("jiemian", len(ps), t)
corpus.append({"source": "jiemian", "id": "13163796", "title": t, "url": "https://www.jiemian.com/article/13163796.html", "paras": ps})

# 3. 豆瓣：整块 <p> 按空行切 stanza
r = get("https://book.douban.com/review/17852978/")
i = r.find("review-content")
raw = strip(r[i : i + 100000])
stanzas = [s for s in re.split(r"\n+", raw) if s.strip()]
ps = keep(stanzas)
t = title_of(r)
print("douban", len(ps), t)
corpus.append({"source": "douban", "id": "17852978", "title": t, "url": "https://book.douban.com/review/17852978/", "paras": ps})

json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in corpus:
    print(c["source"], len(c["paras"]), sum(len(p) for p in c["paras"]), c["title"][:40])
