"""STOP trial：同一管线关 STOP 重渲染 multi 到独立文件，对比 junk 率。
junk 定义：picked span 与 STOP/单字虚词 exact 匹配，或含“为什么/相比于/但是/不是/没有/无法/不要”任一。
"""
import json
import re
import sys

sys.path.insert(0, "eval")
import mvp
import run_multi

JUNK_PAT = re.compile("为什么|相比于|但是|不是|没有|无法|不要|是否|如何|什么|怎么|它们|我们|你们|他们|这些|那些|这个|那个|这里|那里")

mvp.CFG = dict(mvp.CFG)
mvp.CFG["use_stop"] = False
run_multi.main("eval/mvp_multi_nostop.html")

for path in ["eval/mvp_multi.html", "eval/mvp_multi_nostop.html"]:
    h = open(path, encoding="utf-8").read()
    strongs = re.findall(r"<strong>(.*?)</strong>", h)
    junk = [s for s in strongs if s in mvp.STOP or JUNK_PAT.search(s)]
    print(f"{path}: strongs={len(strongs)} junk={len(junk)} rate={len(junk)/max(1,len(strongs)):.3f}")
    print("   e.g.", junk[:12])
