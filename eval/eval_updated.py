
import json
from tqdm import tqdm
from joblib import Parallel, delayed

import os
os.environ['OPENAI_API_KEY'] = ""
from openai import OpenAI


with open("orphanet_hypernym.json", 'r') as f:
    hypernym_data = json.load(f)

hypernym_dict = {}
orphanet_id2name = {}
for item in hypernym_data:
    hypernym_dict[item['name']] = []
    orphanet_id2name[str(item['Orphanetid'])] = item['name']
    for par in item['parents']:
        if par['parent_disease_count'] <= 10:
            hypernym_dict[item['name']].append(par['parent'])

case_id2orphanet_id = {}
case_id2disease = {}
with open("RDS_benchmark.jsonl", 'r') as f:
    for line in f.readlines():
        data = json.loads(line.strip())
        case_id2orphanet_id[str(data['ID'])] = data['orphanetID']
        case_id2disease[str(data['ID'])] = data["diagnosis"]


def get_gpt_result_with_retry(dat):

    client = OpenAI(base_url="")

    final_answer = dat['model_answer']

    if "diagnosis" not in dat:
        dat['diagnosis'] = case_id2disease[str(dat['ID'])]

    score2_set = []
    score2_set.append(dat['diagnosis'])

    score1_set = []
    orphanet_id = str(case_id2orphanet_id[str(dat['ID'])])
    try:
        orphanet_name = orphanet_id2name[orphanet_id]
    except:
        orphanet_name = dat['diagnosis']

    try:
        score1_set.extend(hypernym_dict[orphanet_name])
    except:
        pass
    
    if dat['diagnosis'].lower() != orphanet_name.lower():
        score2_set.append(orphanet_name)

    if len(score1_set) == 0:
        prompt = eval_prompt1.format(answer=final_answer.strip(), score2_set=score2_set)
    else:
        prompt = eval_prompt2.format(answer=final_answer.strip(), score2_set=score2_set, score1_set=score1_set)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
        temperature=0.1,
    )
    result = response.choices[0].message.content

    dat['final_answer'] = final_answer.strip()
    try:
        dat['eval'] = result.strip()
    except:
        dat['eval'] = "1. None: score 0;\n 2. None: score 0;\n3. None: score 0;\n4. None: score 0;\n5. None: score 0."
    with open(output_file, "a") as f:
        f.write(json.dumps(dat, ensure_ascii=False) + '\n')

    return result


answer_dir = ""

with open(answer_dir, 'r') as f:
    data = [json.loads(l) for l in f.readlines()]

output_file = ""

if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['ID'] for g in generated])
    new_data = []
    for d in data:
        if d['ID'] not in generated:
            new_data.append(d)
    data = new_data


eval_prompt1 = """
**Task:** Evaluate the student's answer by comparing it with the reference diagnoses and assign scores according to the criteria below.

**Scoring Criteria:**
- Score 2: Assign this score if the student's answer exactly matches, or is a strict synonym or clear equivalent of, any diagnosis in the Score 2 Set.
- Score 0: Assign this score if the student's answer does not match any diagnosis in the Score 2 set.

**Reference Diagnoses:**
- Score 2 Set: {score2_set}

**Student's Answer:**
{answer}

**Output Format:**
1. Disease 1 name: score X;
2. Disease 2 name: score X;
...
"""

eval_prompt2 = """
**Task:** Evaluate the student's answer by comparing it with the reference diagnoses and assign scores according to the criteria below.

**Scoring Criteria:**
- Score 2: Assign this score if the student's answer exactly matches, or is a strict synonym or clear equivalent of, any diagnosis in the Score 2 Set.
- Score 1: Assign this score only if Score 2 is not met, and the student's answer exactly matches, or is a strict synonym or clear equivalent of, any diagnosis in the Score 1 Set.
- Score 0: Assign this score if the student's answer does not match any diagnosis in either set.

**Reference Diagnoses:**
- Score 2 Set: {score2_set}
- Score 1 Set: {score1_set}

**Student's Answer:**
{answer}

**Output Format:**
1. Disease 1 name: score X;
2. Disease 2 name: score X;
...
"""

results = Parallel(n_jobs=1)(delayed(get_gpt_result_with_retry)(dat) for dat in tqdm(data))