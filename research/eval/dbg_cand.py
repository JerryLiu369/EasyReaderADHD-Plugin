import sys

sys.path.insert(0, "eval")
import mvp

para = "或双方约定不以实际工资作为缴费基数，仅以当地最低缴费基数参缴社保；再如异地代缴。"
segs = mvp.segment_all([para])[0]
print("segs:", [(s["text"], s["off"]) for s in segs])
cand = mvp.build_candidates(para, segs)
for c in cand:
    print(repr(c[2]), c[0], c[1])
