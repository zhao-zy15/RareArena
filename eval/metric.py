import json
import re
import numpy as np


with open("", "r") as f:
    data = [json.loads(l) for l in f.readlines()]
    
top1 = []
top5 = []
for dat in data:
    scores = re.findall(r'score (\d+)', dat['eval'])
    scores = [int(score) for score in scores]
    top1.append(scores[0])
    top5.append(max(scores[:5]))

print(len(top1))
print("Top 1:")
print(np.array(np.bincount(top1)) / len(top1))

print("Top 5:")
print(np.array(np.bincount(top5)) / len(top5))