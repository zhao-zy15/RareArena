# RareArena Collection

To enhance the reproducibility of our benchmark, we provide the scripts of the whole data collection pipeline in this repository.
As descibed in our paper, the dataset collection consists of the following steps:

1. **Case Extraction**

We reproduce [PMC-Patients](https://github.com/zhao-zy15/PMC-Patients) with the 2024 June PMC release using their official codes.
The resulted dataset is now integrated in the offical [PMC-Patient](https://huggingface.co/datasets/THUMedInfo/PMC-Patients) repository as `PMC-Patients-V2.json`.

2. **Case Filtering**

The filtering is conducted in two stages under consideration of API costs.
In the first stage, we use `GPT-4o-mini` to annotate four relatively easy rules, while in the second stage, `GPT-4o` is employed to annotate three complex rules and extract the ground-truth diagnosis.

Simply run `filter_1.py` and `filter_2.py` sequentially to get filtered case reports stored in `filtered.json`.

3. **Mapping Rare Diseases**

To map the ground-truth diagnosis to [Orphanet](https://www.orpha.net/) and filter patients with rare diseases, we employ [`CODER`](https://huggingface.co/GanjinZero/coder_eng) and `GPT-4o` to conduct the mapping.
Specifically, for each ground-truth diagnosis, we use the embedding similarity produced by `CODER` to retrieve top 10 similar disease terms in Orphanet, then use `GPT-4o` to determine whether there is a mapping.

The corresponding code is shown in `mapping.py`.

4. **Trucation and Rephrasing**

This step involves extracting diagnostic test and rephrase the extracted test results and the case report. The code is contained in `rephrase.py`.

5. **Leackage Detection**

We remove any cases with potential leakage using `leakage.py`.

Finally, run `final_output.py` to clean all the temporary labels made during the process and generate benchmark dataset for RDS and RDC respectively.