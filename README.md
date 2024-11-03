# RareArena
A Comprehensive Rare Disease Diagnostic Dataset with nearly 50,000 patients covering more than 4000 diseases.


## Evaluation
To evaluate certain model on RareArena, there are three steps to take:

1. Generate top 5 diagnosis using the model. We provide an OpenAI-style script and our naive prompt used in our paper in `eval/run.py`.

2. Evaluate the top 5 diagnosis using GPT-4o (since it is untrivial to identify whether the true diagnosis is retrieved due to presence of synonyms and hypernyms). The script and prompt for GPT-4o is given in `eval/eval.py`.

3. Parse the evaluation output and calculate top-1 and top-5 recall using `eval/metric.py`.

## Data Collection
To reproduce RareArena, please first reproduce [PMC-Patients](https://github.com/zhao-zy15/PMC-Patients), then follow the pipeline described in our paper. All the prompts can be found in the Supplementary Materials in our paper.

## License
RareArena is released under CC BY-NC-SA 4.0 License.

## Citation
```

```