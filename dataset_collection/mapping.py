
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
import openai
import os
import time


def get_gpt_result_with_retry(prompt, model = "gpt-4o", max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            response = client.chat.completions.create(
                model=model, 
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=4096,
                temperature = 0.1,
            )
            result = response.choices[0].message.content
            return result
        except Exception as e:
            if "filtered" in e.message:
                print("Request filtered!")
                return None
            print(f"Attempt {retries + 1} failed with error: {e}")
            retries += 1
            time.sleep(1) 

    return None


model = SentenceTransformer('GanjinZero/coder_eng')

with open("data/orpha_meta_info.json", 'r') as f:
    meta_info = json.load(f)
orphanet_data = {}
orphanet_syn = {}
definition = {}
for item in meta_info:
    if item['Name'].startswith("OBSOLETE:"):
        continue
    if item['Name'].startswith("OBSELETE:"):
        continue
    if item['Name'].startswith("NON RARE IN EUROPE:"):
        item['Name'] = item['Name'].replace("NON RARE IN EUROPE:", "").strip()
    orphanet_data[item['Name']] = item['OrphaCode']
    orphanet_syn[item['Name']] = item['Name']
    if item['Summary'] != "N/A":
        definition[item['Name']] = item['Summary']
    for syn in item['Synonyms']:
        orphanet_data[syn] = item['OrphaCode']
        orphanet_syn[syn] = item['Name']

orphanet_names = list(orphanet_data.keys())
orphanet_codes = list(orphanet_data.values())
orphanet_embeddings = []
for name in tqdm(orphanet_names):
    emb = model.encode(name.lower(), normalize_embeddings = True)
    orphanet_embeddings.append(emb)
orphanet_embeddings = np.vstack(orphanet_embeddings)


with open("data/filtered.json", "r") as f:
    data = [json.loads(l) for l in f.readlines()]
new_data = []
for dat in data:
    if [dat['Diagnostic Focus'], dat['Clear Single Diagnosis'], dat['Specific Situations']] == ['yes', 'yes', 'no']:
        new_data.append(dat)
data = new_data

output_file = "data/mapped.json"
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['_id'] for g in generated])
    new_data = []
    for d in data:
        if d['_id'] not in generated:
            new_data.append(d)
    data = new_data


def remove_content_in_parentheses(s):
    stack = []  # 用来存储括号及其位置的栈
    result = []  # 用来存储最终结果字符串的列表
    i = 0  # 初始化索引
    for char in s:
        if char == '(':
            stack.append(i)  # 记录'('的位置
        elif char == ')' and stack:
            start = stack.pop()  # 弹出最近一个'('的位置
            if not stack:  # 如果当前栈为空，则说明不在嵌套括号内
                result.append(s[i + 1:])  # 保存当前位置之后的部分
                s = s[:start] + ''.join(result)  # 删除括号及其内的内容
                i = start - 1  # 更新索引位置
                result = []  # 重置结果列表
        i += 1

    # 如果栈不为空，说明有未匹配的'('，需要处理这部分，这里简单地忽略未闭合的'('后的内容
    if stack:
        s = s[:stack[0]]

    return ''.join(result) if result else s


def find_top_10_embeddings(input_vec, embeddings):
    """
    在embeddings中找到与input_vec内积最大的top 10个向量。

    :param input_vec: 输入向量，形状为(768,)
    :param embeddings: 嵌入矩阵，形状为(100, 768)
    :return: 两个列表，分别是top 10向量的索引和对应的内积值
    """
    # 计算输入向量与embeddings每个向量的内积
    scores = np.dot(embeddings, input_vec)
    
    # 获取内积最大的top 10个索引，argsort函数返回的是从小到大的索引，所以用[-10:]来获取最大的10个值的索引
    top_10_indices = np.argsort(scores)[-10:]
    
    # 因为argsort是从小到大排序，为了让Top 1是最大的，我们将索引和分数翻转
    top_10_indices = top_10_indices[::-1]
    top_10_scores = scores[top_10_indices]
    
    return [int(x) for x in top_10_indices], top_10_scores


syn_prompt = """
Whether "{disease1}" and "{disease2}" are synonyms (referring to the same disease)? Only output the answer "YES" or "NO".
"""

subset_prompt = """
Whether "{disease1}" is a subtype or variant of "{disease2}"? Be strict and only answer "YES" if "{disease1}" is completely included in the concept of "{disease2}", and pay extra attention the rareness of two diseases: if "{disease1}" is not a rare disease while "{disease2}" is, output "NO".
Let's think step by step, and carefully compare the two diseases. Respond in JSON format with the following keys:
"reasoning": your reasoning process. 
"answer": "YES" or "NO".
"""


client = openai.AzureOpenAI()

with open(output_file, "a") as f:
    for dat in tqdm(data):
        if type(dat['Final Diagnosis']) != str:
            continue
        try:
            dat['Final Diagnosis'] = remove_content_in_parentheses(dat['Final Diagnosis']).strip()
        except Exception as e:
            print("remove_content_in_parentheses error")
            print(e)
            print(dat)
            print(dat['Final Diagnosis'])
            print(remove_content_in_parentheses(dat['Final Diagnosis']))
            continue

        emb = model.encode(dat['Final Diagnosis'].lower(), normalize_embeddings = True)
        ids, scores = find_top_10_embeddings(emb, orphanet_embeddings)
        if orphanet_names[ids[0]].lower() == dat['Final Diagnosis'].lower():
            dat['OrphaID'] = orphanet_codes[ids[0]]
            f.write(json.dumps(dat, ensure_ascii = False) + '\n')
            continue
        names = []
        new_ids = []
        for i in ids:
            tmp_name = orphanet_syn[orphanet_names[i]]
            if tmp_name in names:
                continue
            names.append(tmp_name)
            new_ids.append(i)

        dat['Orpha_candidates'] = {"ids": new_ids, "names": names}

        match_type = None
        match_candidate = None
        match_reason = None
        for i in range(len(names)):
            response = get_gpt_result_with_retry(syn_prompt.format(disease1 = dat['Final Diagnosis'], disease2 = names[i]), use_json = False)
            if response is None:
                continue
            time.sleep(1)
            if response.strip("\"\'\n., ") == "YES":
                match_type = "synonym"
                match_candidate = names[i]
                break
        
        if match_type is None:
            for i in range(len(names)):
                response = get_gpt_result_with_retry(subset_prompt.format(disease1 = dat['Final Diagnosis'], disease2 = names[i]))
                if response is None:
                    continue
                res = json.loads(response)
                if res['answer'].strip("\"\'\n., ") == 'YES':
                    match_type = "subtype"
                    match_candidate = names[i]
                    match_reason = res['reasoning']
                    break

        if match_type is None:
            f.write(json.dumps(dat) + '\n')
            continue
        dat['match_type'] = match_type
        dat['OrphaName'] = match_candidate
        dat['OrphaID'] = orphanet_data[match_candidate]
        if match_reason:
            dat['match_reason'] = match_reason
        f.write(json.dumps(dat, ensure_ascii = False) + '\n')
