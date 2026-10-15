import re
import sys

sys.path.insert(0, "eval")
import mvp

para = "再如异地代缴。"
segs = mvp.segment_all([para])[0]
print("segs:", [(s["text"], s["off"]) for s in segs])
content = [s for s in segs if mvp.is_content(s)]
print("content:", [(s["text"], s["off"]) for s in content])
cand = mvp.build_candidates(para, segs)
print("cand:", [(c[2], c[0], c[1]) for c in cand])
