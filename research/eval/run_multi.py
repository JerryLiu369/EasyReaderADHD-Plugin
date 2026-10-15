"""多篇 MVP 跑批 + 合并成一个预览 HTML。"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
by_id = {c["id"]: c for c in corpus}

JOBS = [
    ("115568", None),        # 拉伸：v2 同文对比
    ("114821", None),        # 索尼：科技长文
    ("13163796", None),      # 界面：财经政策长文
    ("/ZhengZhi/2026_10_11_903878.shtml", None),  # 观察者：时政社会
    ("17852957", 12),        # 豆瓣书评：取前 12 段（去码后约 7 段实文）
    ("cssn-2022", None),       # 社科网：国关学术长文 46 段（浏览器抓取）
    ("thepaper-7963367", None),  # 澎湃思想市场：历史社会学 33 段（浏览器抓取）
]

def cjk_count(s):
    return sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")


def main(outpath="eval/mvp_multi.html"):
    sections = []
    for cid, limit in JOBS:
        c = by_id[cid]
        paras = c["paras"][:limit] if limit else c["paras"]
        # 正文卫生：CJK 不足 15 的是元数据/模版残留，直接丢
        paras = [p for p in paras if cjk_count(p) >= 15]
        print(f"kept {len(paras)} paras after hygiene")
        inp = f"eval/multi_{c['source']}.txt"
        outp = f"eval/multi_{c['source']}.html"
        open(inp, "w", encoding="utf-8").write("\n".join(paras))
        print(f"=== {c['source']} {c['title'][:40]} n={len(paras)} ===")
        mvp.main(inp, outp)
        body = open(outp, encoding="utf-8").read()
        inner = re.search(r"<body>(.*)</body>", body, re.S).group(1)
        inner = re.sub(r"<header>.*?</header>", "", inner)
        sections.append(
        f"<h1>{c['source']} · {c['title'][:45]}</h1>"
        f"<p class='src'><a href='{c['url']}'>{c['url']}</a>（{len(paras)} 段）</p>" + inner
    )

    doc = (
        "<!DOCTYPE html><html lang='zh'><head><meta charset='utf-8'>"
        "<style>body{max-width:34em;margin:3em auto;line-height:2;font-size:18px;"
        "font-family:system-ui,'PingFang SC','Microsoft YaHei',sans-serif}"
        "strong{font-weight:700;padding:0 .08em}h1{font-size:22px;margin-top:2.5em;border-top:3px solid #333;padding-top:1em}"
        ".src{font-size:13px;color:#888}</style></head><body>"
        + "".join(sections)
        + "</body></html>"
    )
    open(outpath, "w", encoding="utf-8").write(doc)
    u = mvp.usage()
    print(f"wrote {outpath}, total requests:", u["requests"])


if __name__ == "__main__":
    main()
