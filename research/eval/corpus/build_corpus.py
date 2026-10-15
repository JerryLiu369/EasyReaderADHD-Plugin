"""抓 2 篇少数派长文 + 1 篇澎湃新闻，抽正文段落，存 eval/corpus/corpus.json。"""
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"\s+", " ", s).strip()


def sspai_paras(article_id):
    html = get(f"https://sspai.com/post/{article_id}")
    title = strip_tags(re.search(r"<title>(.*?)</title>", html).group(1))
    m = re.search(r'<div class="article-body".*', html, re.S)
    body = m.group(0)[:800000]
    paras = [strip_tags(p) for p in re.findall(r"<p>(.*?)</p>", body, re.S)]
    return title, [p for p in paras if 80 <= len(p) <= 600]


def thepaper_paras(news_id):
    html = get(f"https://www.thepaper.cn/{news_id}")
    title = strip_tags(re.search(r"<title>(.*?)</title>", html).group(1))
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S
    )
    content = json.loads(m.group(1))["props"]["pageProps"]["detailData"][
        "contentDetail"
    ]["content"]
    paras = [strip_tags(p) for p in re.findall(r"<p>(.*?)</p>", content, re.S)]
    return title, [p for p in paras if 80 <= len(p) <= 600]


if __name__ == "__main__":
    home = get("https://sspai.com/")
    ids = sorted(set(re.findall(r"/post/(\d+)", home)))
    print("sspai ids:", ids)
    picked = []
    for aid in ["113843", "114821", "115566"]:
        try:
            t, ps = sspai_paras(aid)
            print(aid, len(ps), t[:50])
            if len(ps) >= 6:
                picked.append(("sspai", aid, t, ps))
        except Exception as e:  # noqa: BLE001
            print("FAIL sspai", aid, str(e)[:150])

    home2 = get("https://www.thepaper.cn/")
    nids = sorted(set(re.findall(r"(newsDetail_forward_\d+)", home2)))
    print("thepaper ids:", nids)
    for nid in nids[:4]:
        try:
            t, ps = thepaper_paras(nid)
            print(nid, len(ps), t[:50])
            if len(ps) >= 6:
                picked.append(("thepaper", nid, t, ps))
                break
        except Exception as e:  # noqa: BLE001
            print("FAIL thepaper", nid, str(e)[:150])

    corpus = [
        {"source": s, "id": i, "title": t, "url": f"https://sspai.com/post/{i}" if s == "sspai" else f"https://www.thepaper.cn/{i}", "paras": ps}
        for s, i, t, ps in picked
    ]
    json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("saved articles:", len(corpus), "total paras:", sum(len(c["paras"]) for c in corpus))
