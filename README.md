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

To reproduce RareArena, see `dataset_collection` directory for all the scripts used in our pipeline.

## Evaluation
To evaluate certain model on RareArena, there are three steps to take:

1. Generate top 5 diagnosis using the model. We provide an OpenAI-style script and our naive prompt used in our paper in `eval/run.py`.

2. Evaluate the top 5 diagnosis using GPT-4o (since it is untrivial to identify whether the true diagnosis is retrieved due to presence of synonyms and hypernyms). The script and prompt for GPT-4o is given in `eval/eval.py`.

3. Parse the evaluation output and calculate top-1 and top-5 recall using `eval/metric.py`.

## Model Performances

### Rare Disease Screening Task

<table>  
  <tr>  
    <th rowspan="2">Model</th>  
    <th colspan="4">Top 1 Recall (%)</th>  
    <th colspan="4">Top 5 Recall (%)</th>  
  </tr>  
  <tr>  
    <th>Score = 0 (missing)</th>  
    <th>Score = 1 (hypernyms)</th>  
    <th>Score = 2 (synonyms)</th>  
    <th>Total*</th>  
    <th>Score = 0 (missing)</th>  
    <th>Score = 1 (hypernyms)</th>  
    <th>Score = 2 (synonyms)</th>  
    <th>Total</th>  
  </tr>  
  <tr>  
    <td>GPT-4o</td>  
    <td>66.95</td>  
    <td>9.93</td>  
    <td>23.13</td>  
    <td>33.05</td>  
    <td>43.14</td>  
    <td>20.26</td>  
    <td>36.61</td>  
    <td>56.86</td>  
  </tr>  
  <tr>  
    <td>Llama3.1-70B</td>  
    <td>74.44</td>  
    <td>8.29</td>  
    <td>17.27</td>  
    <td>25.56</td>  
    <td>52.00</td>  
    <td>17.56</td>  
    <td>30.45</td>  
    <td>48.00</td>  
  </tr>  
  <tr>  
    <td>Qwen2.5-72B</td>  
    <td>75.44</td>  
    <td>10.14</td>  
    <td>14.42</td>  
    <td>24.56</td>  
    <td>49.87</td>  
    <td>23.79</td>  
    <td>26.34</td>  
    <td>50.13</td>  
  </tr>  
  <tr>  
    <td>Gemma2-9B</td>  
    <td>82.09</td>  
    <td>9.75</td>  
    <td>8.16</td>  
    <td>17.91</td>  
    <td>56.01</td>  
    <td>22.90</td>  
    <td>21.09</td>  
    <td>43.99</td>  
  </tr>  
  <tr>  
    <td>Phi3-7B</td>  
    <td>84.31</td>  
    <td>6.11</td>  
    <td>9.58</td>  
    <td>15.69</td>  
    <td>57.61</td>  
    <td>21.15</td>  
    <td>21.24</td>  
    <td>42.39</td>  
  </tr>  
  <tr>  
    <td>Llama3.1-7B</td>  
    <td>86.03</td>  
    <td>6.21</td>  
    <td>7.76</td>  
    <td>13.97</td>  
    <td>58.09</td>  
    <td>19.07</td>  
    <td>22.84</td>  
    <td>41.91</td>  
  </tr>  
  <tr>  
    <td>Qwen2.5-7B</td>  
    <td>86.80</td>  
    <td>7.46</td>  
    <td>5.74</td>  
    <td>13.20</td>  
    <td>55.80</td>  
    <td>29.20</td>  
    <td>15.00</td>  
    <td>44.20</td>  
  </tr>  
</table>  
  
\* Total recall is defined as the sum of score 2 and score 1 matches.

### Rare Disease Confirmation Task
  
<table>  
  <tr>  
    <th rowspan="2">Model</th>  
    <th colspan="4">Top 1 Recall (%)</th>  
    <th colspan="4">Top 5 Recall (%)</th>  
  </tr>  
  <tr>  
    <th>Score = 0 (missing)</th>  
    <th>Score = 1 (hypernyms)</th>  
    <th>Score = 2 (synonyms)</th>  
    <th>Total</th>  
    <th>Score = 0 (missing)</th>  
    <th>Score = 1 (hypernyms)</th>  
    <th>Score = 2 (synonyms)</th>  
    <th>Total</th>  
  </tr>  
  <tr>  
    <td>GPT-4o</td>  
    <td>35.76</td>  
    <td>14.51</td>  
    <td>49.72</td>  
    <td>64.24</td>  
    <td>14.08</td>  
    <td>20.23</td>  
    <td>65.69</td>  
    <td>85.92</td>  
  </tr>  
  <tr>  
    <td>Llama3.1-70B</td>  
    <td>43.94</td>  
    <td>14.41</td>  
    <td>41.66</td>  
    <td>56.06</td>  
    <td>18.43</td>  
    <td>21.12</td>  
    <td>60.45</td>  
    <td>81.57</td>  
  </tr>  
  <tr>  
    <td>Qwen2.5-72B</td>  
    <td>49.46</td>  
    <td>15.46</td>  
    <td>35.09</td>  
    <td>50.54</td>  
    <td>22.98</td>  
    <td>25.93</td>  
    <td>51.09</td>  
    <td>77.02</td>  
  </tr>  
  <tr>  
    <td>Gemma2-9B</td>  
    <td>60.22</td>  
    <td>16.09</td>  
    <td>23.69</td>  
    <td>39.78</td>  
    <td>29.44</td>  
    <td>29.70</td>  
    <td>40.86</td>  
    <td>70.56</td>  
  </tr>  
  <tr>  
    <td>Phi3-7B</td>  
    <td>68.82</td>  
    <td>9.15</td>  
    <td>22.03</td>  
    <td>31.18</td>  
    <td>37.68</td>  
    <td>23.48</td>  
    <td>38.84</td>  
    <td>62.32</td>  
  </tr>  
  <tr>  
    <td>Llama3.1-8B</td>  
    <td>64.14</td>  
    <td>11.17</td>  
    <td>24.69</td>  
    <td>35.86</td>  
    <td>31.13</td>  
    <td>23.84</td>  
    <td>45.03</td>  
    <td>68.87</td>  
  </tr>  
  <tr>  
    <td>Qwen2.5-7B</td>  
    <td>71.78</td>  
    <td>12.68</td>  
    <td>15.54</td>  
    <td>28.22</td>  
    <td>35.08</td>  
    <td>34.08</td>  
    <td>30.85</td>  
    <td>64.92</td>  
  </tr>  
</table>  

## License
RareArena is released under CC BY-NC-SA 4.0 License.

## Acknowledgements  
We would like to acknowledge that the RareArena dataset was created and provided by Tsinghua Medicine, Peking Union Medical College, and Department of Statistics and Data Science at Tsinghua University. 
  

## Citation
Our paper is currently under review at Lancet Digital Health.