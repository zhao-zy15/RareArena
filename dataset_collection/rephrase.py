
import json
import openai
import os
import time
from tqdm import tqdm
import re


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

with open("data/mapped.json", 'r') as f:
    data = [json.loads(l) for l in f.readlines()]

new_data = []
for dat in data:
    if 'OrphaID' not in dat:
        continue
    new_data.append(dat)
data = new_data

output_file = "data/rephrased.json"
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['_id'] for g in generated])
    new_data = []
    for d in data:
        if d['_id'] not in generated:
            new_data.append(d)
    data = new_data

rephrase_prompt = """
As a medical expert specializing in rare diseases, your task is to extract necessary information from a rare disease case summary.

Please follow the instructions step by step:
1. Determine the Diagnostic Examination(s): Identify the diagnostic examination(s) that directly indicate or confirm the diagnosis.
- If the diagnostic examination(s) is/are mentioned, provide its/their standard names. Note that multiple diagnostic examination can be identified in some cases.   
- If the diagnosis in the case report is based on a combination of clinical symptoms and does not rely on specific diagnostic tests, enter "NA" (Not Applicable).

2. Extract the result of the Diagnostic Examination(s). Make sure the results are completely extracted. The extracted result should be complete sentences. Enter "NA", if not applicable.

3. Clean the result of the Diagnostic Examination(s). Keep the clinical findings of the patient and exclude subjective analysis. Enter "NA", if not applicable.

4. Extract all case report details that occur chronologically before before the first diagnostic examination or the first appearance of diagnosis. Do not include any gold standard examination, diagnosis or any details after that. 
- If no diagnostic examination or diagnosis is mentioned, extract all case report details up until the point of official treatment.

Output Format: Provide the results in JSON format with the following keys:
"Diagnostic_examination": string. Diagnostic examination name or "NA".
"Extracted_examination_results": string. Examination results, or "NA".
"Cleaned_examination_results": string. Cleaned examination results, or "NA".
"Extracted_case_report": string. Extracted case results before test/diagnosis.

Here is the diagnosis: {diagnosis}.
Here is the patient summary: 
{summary}
"""

rewrite_prompt = """
Your task is to rephrase a rare disease case summary using your own words while ensuring the rephrased case report meets the following criteria:

1. Focus on Objective Clinical Details: Only include factual information such as laboratory results, imaging findings, physical examination details, and treatments given. Avoid any language that implies or suggests a diagnosis.
2. Exclude Subjective Analysis: Any form of diagnostic language, such as phrases indicating suspicion or implications toward a specific diagnosis, should be completely avoided. The summary should be purely descriptive without any interpretive statements.
3. Do Not Mention the Diagnosis {diagnosis}.
4. Preserve All Clinical Presentations.

Output Format: Provide the results in JSON format with the following keys:
"rewritten_case_report": the rewritten case report. 

Here is the diagnosis: {diagnosis}.
Here is the patient summary: 
{summary}
"""

rewrite_test_prompt = """
Your task is to rephrase a rare disease case summary using your own words while ensuring the rephrased case report meets the following criteria:

1. Focus on Objective Clinical Details: Only include factual information such as laboratory results, imaging findings, physical examination details, and treatments given. Avoid any language that implies or suggests a diagnosis.
2. Exclude Subjective Analysis: Any form of diagnostic language, such as phrases indicating suspicion or implications toward a specific diagnosis, should be completely avoided. The summary should be purely descriptive without any interpretive statements.
3. Avoid Mentioning Diagnostic Procedures: Do not imply or suggest that the patient requires {examination} or any other specific diagnostic procedure.
4. Do Not Mention the Diagnosis {diagnosis}.
5. Preserve All Clinical Presentations.

Output Format: Provide the results in JSON format with the following keys:
"rewritten_case_report": the rewritten case report. 

Here is the diagnosis: {diagnosis}.
Here is the patient summary: 
{summary}
"""

with open(output_file, "a") as f:
    for dat in tqdm(data):
        dat['text'] = re.sub(r'\n', ' ', dat['text'])
        dat['text'] = re.sub(r' +', ' ', dat['text'])
        response = get_gpt_result_with_retry(rephrase_prompt.format(summary = dat['text'], diagnosis = dat['Final Diagnosis']))
        try:
            tmp_result = json.loads(response)
        except Exception as e:
            print(e)
            continue
        dat.update(tmp_result)
        if dat['Diagnostic_examination'] == 'NA':
            response = get_gpt_result_with_retry(rewrite_prompt.format(summary = dat['Extracted_case_report'], diagnosis = dat['Final Diagnosis']))
        else:
            response = get_gpt_result_with_retry(rewrite_test_prompt.format(summary = dat['Extracted_case_report'], diagnosis = dat['Final Diagnosis'], examination = dat['Diagnostic_examination']))
        try:
            dat.update(json.loads(response))
        except Exception as e:
            print(e)
            continue
        dat['rewritten_case_report'] = re.sub(r'\n', ' ', dat['rewritten_case_report'])
        dat['rewritten_case_report'] = re.sub(r' +', ' ', dat['rewritten_case_report'])
        f.write(json.dumps(dat, ensure_ascii = False) + '\n')
        