"""全库重提：阈值统一 40（ nomination 80 漏正文），文章内去重。按 corpus.json 存的 URL 重抓。"""
import json
import re
import sys
import urllib.request

sys.path.insert(0, "eval/corpus")
from build_corpus import strip_tags  # noqa

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
MINLEN = 40


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def keep(ps):
    out = []
    for p in (re.sub(r"\s+", " ", p).strip() for p in ps):
        if MINLEN <= len(p) <= 600:
            out.append(p)
    return out


def dedup(ps):
    seen, out = set(), []
    for p in ps:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def title_of(h):
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    from build_corpus import strip_tags as st

    return st(m.group(1))[:60] if m else "?"


corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
for c in corpus:
    url = c["url"]
    try:
        if c["source"] == "sspai":
            h = get(url)
            m = re.search(r'<div class="article-body".*', h, re.S)
            inners = re.findall(r"<p>(.*?)</p>", m.group(0)[:800000], re.S)
            ps = [p for p in (strip_tags(x) for x in inners) if MINLEN <= len(p) <= 600]
        elif c["source"] == "jiemian":
            h = get(url)
            i = h.find("article-content")
            inners = re.findall(r"<p[^>]*>(.*?)</p>", h[i : i + 200000], re.S)
            clean = [re.sub(r"\s+", " ", re.sub(r"<[a-zA-Z/][^>]*>", "", x)).strip() for x in inners]
            ps = [p for p in clean if MINLEN <= len(p) <= 600]
        elif c["source"] == "guancha":
            h = get(url)
            i = h.find("all-txt")
            ps = [strip_tags(p) for p in re.findall(r"<p>(.*?)</p>", h[i : i + 300000], re.S)]
            ps = [p for p in ps if MINLEN <= len(p) <= 600]
        elif c["source"] == "douban":
            h = get(url)
            i = h.find("review-content")
            seg = re.sub(r"<[^>]+>", "\n", h[i : i + 100000])
            stanzas = [s for s in re.split(r"\n+", seg) if s.strip()]
            ps = [re.sub(r"\s+", " ", p).strip() for p in stanzas]
            ps = [p for p in ps if MINLEN <= len(p) <= 600]
        else:
            continue
        ps = dedup(ps)
        print(f"{c['source']} {c['id']}: {len(c['paras'])} -> {len(ps)}")
        c["paras"] = ps
    except Exception as e:  # noqa: BLE001
        print("FAIL", c["source"], c["id"], str(e)[:150])
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
