# Towards Automatic Evaluation for LLMs' Clinical Capabilities: Metric, Data, and Algorithm
[查看中文版本](https://github.com/Alipay-Med/SPs_benchmark/blob/main/README_cn.md)

## SPs Benchmark Overview
The standardized patients (SPs) benchmark contains three important aspects towards automatic evaluation for LLMs' clinical capabilities:
- **Evaluation Metrics**: Information Completeness, Behavior Standardization, Guidance Rationality, Diagnostic Logicality, Treatment Logicality, and Clinical Applicability.
- **RJUA-SPs Dataset**: Virtual medical records for 45 simulated standardized patients (covering complete medical information for diagnosis and treatment).
- **Algorithm**: A multi-agent framework for simulating the clinical conversations.

![image](https://github.com/Alipay-Med/SPs_benchmark/pic/tease-1.png)


## Collaborating Institutions
- **Ant Group**
- **Department of Urology of Renji Hospital, affiliated with Shanghai Jiao Tong University School of Medicine**


## RJUA-SPs Dataset

### Overview
The RJUA-SPs (RenJi hospital department of Urology and Ant Group collaborative standardized patients dataset). This dataset is a collaborative creation by the AntGroup Medical LLM (Large Language Model) team and the expert team from the Department of Urology at Renji Hospital, affiliated with Shanghai Jiao Tong University School of Medicine. 

### A SP Example
A simplified example of structural SPs' medical records. Some details are omitted due to the limited space, such as the report results (denoted by XXX). Category and item are for bi-level retrieval, respectively. For a data sample, please refer to test_case.xlsx.

![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/SPs_template-1.png)

### Dataset Features
Characteristics of RJUA-SPs dataset. The data come from virtual cases written by medical experts based on clinical experience, making the dataset more realistic and ensuring data privacy. The questions cover multiple aspects of urology, accounting for 95% of all urological diseases. The dataset provides detailed specialty evidence and reasoning processes.

Based on this dataset, evaluations can be performed for various of medical tasks:
- **Single-turn Clinical QA**
- **Multi-turn Diagnostic Dialogue**
- **Clinical Diagnostic Reasoning**

The retrieval task is used to construct data format, which can be further exploited for automatic evaluations. The data source of the retrieval task is from SPs data.

![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/tasks-1.png)


### Metric Information
The evaluation metrics (LLM-specific clinical pathway). The capabilities are derived from the clinical practice pathway, which induces the principles of data collection. Retrieval-Augmented Evaluation (RAE) can achieve an automatic evaluation algorithm via the retrieval task.

| **Metric**             | **SPs Data**           | **Algorithm**          | **Capability**                                       |
|------------------------|------------------------|------------------------|------------------------------------------------------|
| Information Completeness | **(S)**, **(T)**, **(E)** | How much SPs' info is retrieved. | Enquire medical information of patients. |
| Behavior Standardization | **(O)**                | Whether following the retrieved inquiry order. | Enquire information by a suitable order.  |
| Guidance Rationality    | **(T)**, **(E)**        | How many reasonable tests/exams are retrieved. | Enquire reasonable test/exam reports.  |
| Diagnostic Logicality   | **(R)**                | Generations VS. Retrieved ground-truth. | Reason out the correct diagnosis results.  |
| Treatment Logicality    | **(R)**                | Generations VS. Retrieved ground-truth. | Reason out the correct treatment plans.    |
| Clinical Applicability   | **(Rd)**               | Agent's round VS. Retrieved clinician's round | Finishing tasks within reasonable consultation rounds. |

### Algorithm
Overview of the multi-agent framework. Intent recognition aims to understand the doctor agent's query for terminating conversation. Query parser can map the doctor agent's query to bi-level structure. The multi-agent framework can achieve context generation for the clinical QA and reasoning tasks, as well as environment simulation for the diagnostic dialogue tasks. Besides, RAE can automatically evaluate the doctor agent's clinical capabilities.

![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/multi-agent-frame-1.png)


## Usage Instructions

### Evaluation tasks

- **Single-turn Clinical QA**

```bash
python eval_qa.py
```

- **Multi-turn Diagnostic Dialogue**

```bash
python eval_diag.py
```

- **Clinical Diagnostic Reasoning**

```bash
python eval_reason.py
```


### Citation

If you find our work helpful and have used our dataset, please cite the following description. We will continue to optimize the dataset and update the citable arXiv paper.

```bibtex
@misc{liu2024automatic,
      title={Towards Automatic Evaluation for LLMs' Clinical Capabilities: Metric, Data, and Algorithm}, 
      author={Lei Liu and Xiaoyan Yang and Fangzhou Li and Chenfei Chi and Yue Shen and Shiwei Lyu and Ming Zhang and Xiaowei Ma and Xiangguo Lyu and Liya Ma and Zhiqiang Zhang and Wei Xue and Yiran Huang and Jinjie Gu},
      year={2024},
      eprint={2403.16446},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

### Download
You can download the complete dataset from the [link](https://www.atecup.cn/dataSetDetailOpen/51) at ATEC.

For any questions or suggestions about the dataset, please contact us at: [liulei1497@gmail.com](liulei1497@gmail.com), [joyce.yxy@antgroup.com](joyce.yxy@antgroup.com), [chichenfei@renji.com](chichenfei@renji.com), [huangyiran@renji.com](huangyiran@renji.com), [zhanying@antgroup.com](zhanying@antgroup.com)

**Note**: When using the dataset, please ensure compliance with relevant laws, regulations, and data privacy policies.

### Contributors
Lei Liu, Xiaoyan Yang, Shiwei Lyu, Yue Shen, Zhiqiang Zhang, Cong Fan, Dongjie Tao, Jinjie Gu

Chenfei Chi, Fangzhou Li, Xiaowei Ma, Xiangguo Lyu, Ming Zhang, Liya Ma, Jiaye Pan, Wei Xue, Yiran Huang

Zixiao Chen, Shuai Zhen, Xiaoli Xu, Guangsheng Zhou, Zhipan Chen, Kaiyan Jiang

### Licence Information
The codes in this repo are available under GNU Affero General Public License. The dataset is available under Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0), which means you may not use the dataset for commercial purposes, and if you remix, transform, or build upon the dataset, you must distribute your contributions under the same license.