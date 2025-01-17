# RareArena
A Comprehensive Rare Disease Diagnostic Dataset with nearly 50,000 patients covering more than 4000 diseases.

## Data Collection
We build our work upon [PMC-Patients](https://github.com/zhao-zy15/PMC-Patients), a large-scale patient summary dataset sourced from PMC case reports, and we use GPT-4o for all data processing.

To be specific, we first filter cases focusing on rare disease diagnoses from PMC-Patients, and extract their ground-truth diagnosis.
Then we map each diagnosis to the Orphanet database using [CODER](https://github.com/GanjinZero/CODER) term embeddings, and filter out the cases with diagnosis failing to map.
Next, we truncate the cases and rephrased them to avoid diagnosis leakage.
Here we consider two task settings:
- Rare Disease Screening (RDS), where the cases are truncated up to any diagnosic tests, such as whole-genome sequencing for genetic diseases and pathogen detection for rare infections.
- Rare Disease Confirmation (RDC), where the cases are truncated up to the final diagnosis.
Finally, we remove any cases with potential diagnosis leakage.

## Evaluation
To evaluate certain model on RareArena, there are three steps to take:

1. Generate top 5 diagnosis using the model. We provide an OpenAI-style script and our naive prompt used in our paper in `eval/run.py`.

2. Evaluate the top 5 diagnosis using GPT-4o (since it is untrivial to identify whether the true diagnosis is retrieved due to presence of synonyms and hypernyms). The script and prompt for GPT-4o is given in `eval/eval.py`.

3. Parse the evaluation output and calculate top-1 and top-5 recall using `eval/metric.py`.

## Model Performances

|  <th align="center" colspan="4"> Top 1 Recall (%)  <th align="center" colspan="4"> Top 5 Recall (%) |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
|  | Score = 0 (missing) | Score = 1 (hypernyms) | Score = 2 (synonyms) | Total* | Score = 0 (missing) | Score = 1 (hypernyms) | Score = 2 (synonyms) | Total |
| GPT-4o | 66.95 | 9.93 | 23.13 | 33.05 | 43.14 | 20.26 | 36.61 | 56.86 |
| Llama3.1-70B | 74.44 | 8.29 | 17.27 | 25.56 | 52.00 | 17.56 | 30.45 | 48.00 |
| Qwen2.5-72B | 75.44 | 10.14 | 14.42 | 24.56 | 49.87 | 23.79 | 26.34 | 50.13 |
| Gemma2-9B | 82.09 | 9.75 | 8.16 | 17.91 | 56.01 | 22.90 | 21.09 | 43.99 |
| Phi3-7B | 84.31 | 6.11 | 9.58 | 15.69 | 57.61 | 21.15 | 21.24 | 42.39 |
| Llama3.1-7B | 86.03 | 6.21 | 7.76 | 13.97 | 58.09 | 19.07 | 22.84 | 41.91 |
| Qwen2.5-7B | 86.80 | 7.46 | 5.74 | 13.20 | 55.80 | 29.20 | 15.00 | 44.20 |

\* Total recall is defined as the sum of score 2 and score 1 matches.

|  <th align="center" colspan="4"> Top 1 Recall (%) <th align="center" colspan="4">  Top 5 Recall (%) |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
|  | Score = 0 (missing) | Score = 1 (hypernyms) | Score = 2 (synonyms) | Total | Score = 0 (missing) | Score = 1 (hypernyms) | Score = 2 (synonyms) | Total |
| GPT-4o | 35.76 | 14.51 | 49.72 | 64.24 | 14.08 | 20.23 | 65.69 | 85.92 |
| Llama3.1-70B | 43.94 | 14.41 | 41.66 | 56.06 | 18.43 | 21.12 | 60.45 | 81.57 |
| Qwen2.5-72B | 49.46 | 15.46 | 35.09 | 50.54 | 22.98 | 25.93 | 51.09 | 77.02 |
| Gemma2-9B | 60.22 | 16.09 | 23.69 | 39.78 | 29.44 | 29.70 | 40.86 | 70.56 |
| Phi3-7B | 68.82 | 9.15 | 22.03 | 31.18 | 37.68 | 23.48 | 38.84 | 62.32 |
| Llama3.1-8B | 64.14 | 11.17 | 24.69 | 35.86 | 31.13 | 23.84 | 45.03 | 68.87 |
| Qwen2.5-7B | 71.78 | 12.68 | 15.54 | 28.22 | 35.08 | 34.08 | 30.85 | 64.92 |


## License
RareArena is released under CC BY-NC-SA 4.0 License.

## Acknowledgements  
We would like to acknowledge that the RareArena dataset was created and provided by Tsinghua Medicine, Peking Union Medical College, and Department of Statistics and Data Science at Tsinghua University. 
  

## Citation
Our paper is currently under review at Lancet Digital Health.
