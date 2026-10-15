import json
import sys

sys.path.insert(0, "eval/corpus")
from build_corpus import sspai_paras

t, ps = sspai_paras("115568")
print(t, len(ps))
corpus = json.load(open("eval/corpus/corpus.json", encoding="utf-8"))
corpus.append(
    {"source": "sspai", "id": "115568", "title": t, "url": "https://sspai.com/post/115568", "paras": ps}
)
json.dump(corpus, open("eval/corpus/corpus.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open("eval/mvp_input.txt", "w", encoding="utf-8").write("\n".join(ps))
print("paras:", len(ps), "chars:", sum(len(p) for p in ps))
