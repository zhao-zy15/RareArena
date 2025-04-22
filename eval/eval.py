
import json
import openai
import os
import time
from tqdm import tqdm


openAI_key = ""
client = openai.OpenAI(api_key=openAI_key)

def get_gpt_result_with_retry(prompt, model = "gpt4o", max_retries = 3):
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


answer_dir = ""
with open(answer_dir, 'r') as f:
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

eval_prompt = """
You are an expert in rare disease field. You will receive a student's answer containing 5 differential diagnoses, as well as the reference diagnosis. You need to score each diagnosis from the student's answer according to the following rules:

2 = The student’s diagnosis exactly matches the reference diagnosis; 
1 = The student’s diagnosis is a broad category that includes the reference diagnosis; 
0 = The student's diagnosis does not meet the criteria for a score of 1 or 2.

Here is the student’s answer: 
{answer}

Here is the reference diagnosis: 
{diagnosis}

Output Format: Output the scores in the following format. 
1. Disease 1 name: score X;
2. Disease 2 name: score X;
...
"""

with open(output_file, "a") as f:
    for dat in tqdm(data):
        try:
            response = get_gpt_result_with_retry(eval_prompt.format(answer = dat['answer'], diagnosis = dat['diagnosis']))
        except Exception as e:
            print(e)
            continue
        if response is None:
            continue
        dat['eval'] = response.strip()
        f.write(json.dumps(dat, ensure_ascii = False) + '\n')
        
