
import json
import openai
import os
import time
from tqdm import tqdm
import sys


openAI_key = ""
client = openai.OpenAI(api_key=openAI_key)

def get_gpt_result_with_retry(prompt, model = "", max_retries=1, use_json = True):
    retries = 0
    while retries < max_retries:
        try:
            if use_json:
                response = client.chat.completions.create(
                    model=model, 
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=4096,
                    temperature = 0.1,
                )
            else:
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
            if hasattr(e, "message") and "filtered" in e.message:
                print("Request filtered!")
                return None
            print(f"Attempt {retries + 1} failed with error: {e}")
            retries += 1
            time.sleep(1) 

    return None


data_dir = ""
with open(data_dir, 'r') as f:
    data = [json.loads(l) for l in f.readlines()]

output_file = ""
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['_id'] for g in generated])
    new_data = []
    for d in data:
        if d['_id'] not in generated:
            new_data.append(d)
    data = new_data
split_num = int(sys.argv[1])
index = int(sys.argv[2])
split = (len(data) // split_num) + 1
data = data[(index * split) : min(((index+1) * split), len(data))]

answer_prompt = """
As an expert in rare disease field, enumerate top 5 most likely diagnosis for the following patient in order, with the most likely disease output first. Only consider rare diseases.

Here is the case: 
{case}

Only output the diagnosis in numeric order, one per line. For example:
1. Disease A;
2. Disease B;
...

Do not output anything else!
"""

with open(output_file, "a") as f:
    for dat in tqdm(data):
        try:
            # RDS task
            case = dat['case_report']
            # RDC task
            # case = dat['case_report'] + ' ' + dat['test_results']
            response = get_gpt_result_with_retry(answer_prompt.format(case = case), use_json = False)
        except Exception as e:
            print(e)
            continue
        if response is None:
            continue
        f.write(json.dumps({"_id": dat['_id'], "answer": response.strip(), "diagnosis": dat['diagnosis']}, ensure_ascii = False) + '\n')
        