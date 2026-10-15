import sys

sys.path.insert(0, "eval")
import mvp

text = "我们发现查尔斯·蒂利（Charles Tilly）在20世纪80年代提出"
segs = mvp.segment_all([text])[0]
print("segs:", [(s["text"], s["off"]) for s in segs])
cand = mvp.build_candidates(text, segs)
for c in cand:
    print(repr(c[2]), c[0], c[1])
gap_i = text.find("·")
print("sep char:", hex(ord(text[gap_i])), repr(text[gap_i]))
