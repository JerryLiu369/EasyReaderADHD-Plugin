"""前LLM探针：韩寒 2012/2013 博客（叙事+议论），22 段，同一 v3 管线无调整。"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp

corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
arts = [c for c in corpus if c.get("era") == "preLLM"]
print("preLLM articles:", [(a["id"], len(a["paras"])) for a in arts])

# 我的标（job 按文章顺序排）
labels = json.load(open("eval/prellm_labels.json", encoding="utf-8"))
# 打印各方含的段数，校验
allparas = []
for a in arts:
    allparas.extend(a["paras"])
print("total paras:", len(allparas))
# 标只覆盖关键段（H6/H7 = 地震思考录），先看实际段落匹配
for lab in labels:
    k = lab["keys"][0]
    hit = [i for i, p in enumerate(allparas) if k in p]
    print(lab["job"], "first key", k, "-> paras", hit[:3])
