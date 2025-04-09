import json
import openai
import os
import time
from tqdm import tqdm


client = openai.AzureOpenAI()


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


with open("data/rephrased.json", 'r') as f:
    data = [json.loads(l) for l in f.readlines()]
new_data = []
for dat in data:
    if len(dat['rewritten_case_report'].split()) >= 50:
        new_data.append(dat)
data = new_data

output_file = "data/leakage_removed.json"
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['_id'] for g in generated])
    new_data = []
    for d in data:
        if d['_id'] not in generated:
            new_data.append(d)
    data = new_data

case_prompt = """
Your task is to determine if there is leakage in a rare disease diagnosis task.
Your job is to check if the disease, or its synonyms, or abbreviations, are mentioned in the case. You should focus solely on the literal wording, not the medical interpretation.
Here is the disease: {diagnosis}
Here is the case: {case} 
Output only "yes" or "no". 
"""

test_prompt = """
Your task is to determine if there is leakage in a rare disease diagnosis task.
Your job is determining whether the test result below mentions the diagnosis, or its synonyms (or abbreviation). You should focus solely on the literal wording, not the medical interpretation.
Here is the diagnosis: {diagnosis}.
Here is the result: {result}

Output only "yes" or "no".
"""


with open(output_file, "a") as f:
    for dat in tqdm(data):
        response = get_gpt_result_with_retry(case_prompt.format(case = dat['rewritten_case_report'], diagnosis = dat['Final Diagnosis']), use_json = False)
        if response is None:
            continue
        response = response.strip("\n.").lower()
        dat['case_leakage'] = response
        if dat['Cleaned_examination_results'] != "NA":
            response = get_gpt_result_with_retry(test_prompt.format(result = dat['Cleaned_examination_results'], diagnosis = dat['Final Diagnosis']), use_json = False)
            if response is None:
                continue
            response = response.strip("\n.").lower()
            dat['result_leakage'] = response
        
        f.write(json.dumps(dat, ensure_ascii = False) + '\n')
        