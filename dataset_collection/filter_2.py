
import json
import openai
import os
import time
from tqdm import tqdm


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

def extract_json_from_markdown(markdown_content):
    # 搜索 JSON 开始的标记
    start_marker = "```json"
    end_marker = "```"
    
    # 查找开始和结束的索引位置
    start_index = markdown_content.find(start_marker)
    end_index = markdown_content.find(end_marker, start_index + len(start_marker))
    
    if start_index != -1 and end_index != -1:
        # 提取 JSON 字符串
        json_content = markdown_content[start_index + len(start_marker):end_index].strip()
        return json_content
    else:
        # 如果找不到，返回空字符串或者错误信息
        return "JSON content not found or incorrect markdown format."


client = openai.AzureOpenAI()

with open("data/temp_filtered.json", 'r') as f:
    data = [json.loads(l) for l in f.readlines()]
new_data = []
for dat in data:
    if dat['single_patient'] == 'yes' and dat['human'] == 'yes' and dat['diagnosis_before_death'] == 'yes' and dat['diagnosis_after_birth'] == 'yes':
        new_data.append(dat)
data = new_data

output_file = "data/filtered.json"
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['_id'] for g in generated])
    new_data = []
    for d in data:
        if d['_id'] not in generated:
            new_data.append(d)
    data = new_data


filter_prompt = """
As the editor of the "Rare Disease Diagnostics" column for a top-tier medical journal, your primary responsibility for this session is to review case reports submitted to the column. This column aims to publish comprehensive accounts of the diagnostic process for rare diseases. To ensure that case reports meet our standards, please follow the specific evaluation guidelines below:

1. **Diagnostic Focus**: Verify whether the case report primarily focuses on the diagnostic process rather than treatment, surgery, evolution, or complications of the primary disease.
   
2. **Clear Single Diagnosis**: Confirm whether the case report clearly presents a single diagnostic outcome. Although the diagnostic journey may include misdiagnoses or differential diagnoses, the outcome must not combine diagnoses.

3. **Specific Situations**: Determine if the primary rare disease diagnosis is any of the following situations: metastatic tumor, secondary complications of other diseases or trauma, and side effects of the treatment.

Let's think step by step. At the end of your response, summarize your judgments in a JSON dict with the following keys:
Diagnostic Focus: yes/no, indicating whether the case report focuses on the diagnostic process
Clear Single Diagnosis: yes/no, indicating whether a clear single diagnosis of a rare disease is provided
Specific Situations: yes/no, indicating whether the case reports fit the specific situations. 
Final Diagnosis: if applicable, state the final diagnosis with its standardized disease name. 


Here is a submitted case report to be reviewed:
Title:
{title}

Case Report:
{note}
"""

with open(output_file, "a") as f:
    for dat in tqdm(data):
        retry = 0
        while retry < 3:
            response = get_gpt_result_with_retry(filter_prompt.format(note = dat['text'], title = dat['title']))
            try:
                tmp_result = json.loads(extract_json_from_markdown(response))
            except json.decoder.JSONDecodeError as e:
                print(e)
                retry += 1
                continue
            dat.update(tmp_result)
            f.write(json.dumps(dat, ensure_ascii = False) + '\n')
            break

