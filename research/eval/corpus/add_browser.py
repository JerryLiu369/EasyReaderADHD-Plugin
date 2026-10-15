"""浏览器抓的两篇长文入库：社科网大国竞争（46段）、严飞历史社会学（33段）。"""
import json

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))


def load_txt(path):
    t = open(path, encoding="utf-8").read().split("\n\n")
    return [x.strip() for x in t if x.strip()]


corpus.append({
    "source": "cssn",
    "id": "cssn-2022",
    "title": "大国竞争的根源：基于报酬递增机制的分析（田野，《中国社会科学》2022年第9期）",
    "url": "https://www.cssn.cn/dkzgxp/zgxp_zgshkx/2022nd9q/202210/t20221028_5556553.shtml",
    "paras": load_txt("eval/corpus/raw/cssn.txt"),
})
corpus.append({
    "source": "thepaper",
    "id": "thepaper-7963367",
    "title": "严飞：历史、社会与历史社会学",
    "url": "https://www.thepaper.cn/newsDetail_forward_7963367",
    "paras": load_txt("eval/corpus/raw/yanfei.txt"),
})
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for c in corpus[-2:]:
    print(c["source"], len(c["paras"]), sum(len(p) for p in c["paras"]))
