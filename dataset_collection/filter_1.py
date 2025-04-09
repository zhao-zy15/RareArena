
import json
import openai
import os
import time
from tqdm import tqdm


def get_gpt_result_with_retry(prompt, model = "gpt4o-mini", max_retries=5):
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


data_dir = "" # Directory to PMC-Patients-V2.json
data = json.load(open(data_dir, "r"))

output_file = "data/temp_filtered.json"
if os.path.exists(output_file):
    with open(output_file, 'r') as f:
        generated = [json.loads(line) for line in f.readlines()]
    generated = set([g['_id'] for g in generated])
    new_data = []
    for d in data:
        if d['patient_uid'] not in generated:
            new_data.append(d)
    data = new_data

filter_prompt = """
Please assess the following clinical case report to determine the following points:
1. Whether the report involves only one patient;
2. Whether the case is focusing on a human being;
3. Whether the patient is diagnosed before death;
4. Whether the patient is diagnosed after birth, i.e. exclude infants with gene defect detected before birth.

Case Report:
{note}

Let's think step by step. At the end of your response, summarize your judgments in a JSON dict with the following keys:
single_patient: yes/no
human: yes/no
diagnosis_before_death: yes/no
diagnosis_after_birth: yes/no
"""

client = openai.AzureOpenAI()

with open(output_file, "a") as f:
    for dat in tqdm(data):
        retry = 0
        while retry < 3:
            response = get_gpt_result_with_retry(filter_prompt.format(note = dat['text']))
            if not response:
                break
            try:
                tmp = json.loads(extract_json_from_markdown(response))
            except json.decoder.JSONDecodeError as e:
                print(e)
                retry += 1
                continue
            patient = {"_id": dat['patient_uid'], "PMID": dat['PMID'], "title": dat['title'], "text": dat['patient'], "pub_date": dat['pub_date'], "age": dat['age'], "gender": dat['gender']}
            patient.update(tmp)
            f.write(json.dumps(dat, ensure_ascii = False) + '\n')
            break

