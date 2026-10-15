"""前大模型时代探针语料：
1) 韩寒《春萍，我做到了》2012-11（博客/叙事随笔）
2) 韩寒《地震思考录》2013-04（博客/议论）
3) 和菜头《ZION》2006-03（博客/技术随笔）
统一解 sina 博客正文（div + br 混排），入库 eval/corpus/corpus.json（era: preLLM）。
"""
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


def sina_paras(pid):
    h = get(f"http://blog.sina.com.cn/s/{pid}")
    m = re.search(r'id="sina_keyword_ad_area2"[^>]*>(.*?)</div>\s*<!--', h, re.S)
    body = m.group(1) if m else ""
    # div 与 br 都当段落界线
    chunks = re.split(r"</?[Dd][Ii][Vv][^>]*>|<br\s*/?>", body)
    out = []
    for p in (strip(c) for c in chunks):
        if not p:
            continue
        if "新浪BLOG意见反馈" in p or "About Sina" in p or "article-list" in p:
            continue
        if len(p) < 80:
            continue
        # 超长段按句切成 600 内
        if len(p) > 600:
            sents, cur = [], ""
            for ch in p:
                cur += ch
                if ch in "。！？" and len(cur) >= 100:
                    sents.append(cur)
                    cur = ""
            if cur:
                sents.append(cur)
            out.extend([s for s in sents if len(s) >= 80][:12])
        else:
            out.append(p)
    return out


JOBS = [
    ("blog_4701280b0102ec39", "韩寒《春萍，我做到了》(2012-11)"),
    ("blog_4701280b0102egl0", "韩寒《地震思考录》(2013-04)"),
    ("blog_53f02cd2010003t1", "和菜头《ZION》(2006-03)"),
]

if __name__ == "__main__":
    corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
    corpus = [c for c in corpus if c["source"] != "sina-blog"]
    for pid, title in JOBS:
        try:
            ps = sina_paras(pid)
            print(f"{title}: {len(ps)} paras", "chars:", sum(len(p) for p in ps))
            if ps:
                corpus.append({
                    "source": "sina-blog", "id": pid, "title": title,
                    "url": f"http://blog.sina.com.cn/s/{pid}", "paras": ps, "era": "preLLM",
                })
        except Exception as e:  # noqa: BLE001
            print("FAIL", pid, str(e)[:150])
    json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("articles:", len(corpus))
