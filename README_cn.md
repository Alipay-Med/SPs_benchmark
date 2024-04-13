# 大型语言模型（LLMs）临床能力自动评测框架：指标、数据和算法
[English Version](https://github.com/Alipay-Med/SPs_benchmark/blob/main/README.md)
## 标准化患者大模型评测基准
标准化病人(SP)基准包括针对大型语言模型（LLMs）临床能力自动评估的三个重要方面：
- **评估指标**：信息完整性、行为标准化、指导合理性、诊断逻辑性、治疗逻辑性和临床适用性。
- **RJUA-SPs 数据集**：45个模拟标准化病人的虚拟医疗记录（涵盖诊断和治疗的完整医疗信息）。
- **算法框架**：模拟临床对话的多智能体框架。

![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/tease-1.png)


## 合作机构
- **蚂蚁集团**
- **上海交通大学医学院附属仁济医院泌尿外科**

## RJUA标准化患者数据集

### 数据集概况

RJUA-SPs数据集 (RenJi hospital department of Urology and Antgroup collaborative standardized patients dataset)由蚂蚁集团医疗大语言模型(LLM)团队与上海交通大学医学院附属仁济医院泌尿外科的专家团队共同构建。

### 标准化患者数据集样例

一个简化的结构化标准化患者(SP)医疗记录示例。由于空间有限，省略了一些内容的细节，例如报告结果（用XXX表示）。类别和项目分别用于两级检索。具体信息请参考 test_case.xlsx 示例文件。

![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/SPs_template-1.png)


### 数据集特征
数据来源于医学专家基于临床经验编写的虚拟案例，使得数据集更加真实并确保了数据隐私。问题覆盖了泌尿科的多个方面，涵盖95%的泌尿病症。数据集提供了详细的专业证据和推理过程。
基于该数据集，可以对多种医疗任务进行评测。

- **单轮临床问答**
- **多轮诊断对话**
- **临床诊断推理**

下图展示了不同类型医疗任务的构造示例。检索任务利用标准化患者数据构建数据不同医疗任务的数据格式，以用于进一步的自动评估。

![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/tasks-1.png)


### 指标信息
SPs基准评估范式：评估能力的要求主要来自于LCP（基于大模型的特定临床路径），该要求也决定了数据采集的要求。RAE(检索增强评测框架)通过检索任务来实现自动化的评测算法。

| **Metric**             | **SPs Data**           | **Algorithm**          | **Capability**                                       |
|------------------------|------------------------|------------------------|------------------------------------------------------|
| Information Completeness | **(S)**, **(T)**, **(E)** | How much SPs' info is retrieved. | Enquire medical information of patients. |
| Behavior Standardization | **(O)**                | Whether following the retrieved inquiry order. | Enquire information by a suitable order.  |
| Guidance Rationality    | **(T)**, **(E)**        | How many reasonable tests/exams are retrieved. | Enquire reasonable test/exam reports.  |
| Diagnostic Logicality   | **(R)**                | Generations VS. Retrieved ground-truth. | Reason out the correct diagnosis results.  |
| Treatment Logicality    | **(R)**                | Generations VS. Retrieved ground-truth. | Reason out the correct treatment plans.    |
| Clinical Applicability   | **(Rd)**               | Agent's round VS. Retrieved clinician's round | Finishing tasks within reasonable consultation rounds. |

### 算法框架
多智能体框架概述：意图识别旨在理解医生智能体用于结束对话的查询。查询理解可以将医生智能体的查询映射到双层结构。该多智能体框架可以为临床问答和推理任务实现上下文生成，以及为诊断对话任务提供环境模拟。此外，RAE可以自动评估医生智能体的临床能力。
![image](https://github.com/Alipay-Med/SPs_benchmark/blob/main/pic/multi-agent-frame-1.png)


## 使用说明

### 评测任务

- **单轮临床问答**

```bash
python eval_qa.py
```

- **多轮诊断对话**

```bash
python eval_diag.py
```

- **临床诊断推理**

```bash
python eval_reason.py
```


### 引用

如果您发现我们的工作有帮助，并且使用了我们的数据集，请引用以下描述。我们将继续优化数据集并更新可引用的arXiv论文。

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

### 下载
你可以通过[下载链接](https://www.atecup.cn/dataSetDetailOpen/51) ，在ATEC平台上获取完整的数据集。

如果对数据集和评测框架有任何的问题或者建议，欢迎通过以下方式联系我们：
 [liulei1497@gmail.com](liulei1497@gmail.com), [joyce.yxy@antgroup.com](joyce.yxy@antgroup.com), [chichenfei@renji.com](chichenfei@renji.com), [huangyiran@renji.com](huangyiran@renji.com), [zhanying@antgroup.com](zhanying@antgroup.com)

**注意**：使用数据集时，请确保遵守相关法律法规和数据隐私政策。

### 参与人员
刘磊，杨晓燕，吕世伟，申月，张志强，樊聪，陶东杰，顾进杰

迟辰斐、李方舟、马硝惟、吕向国、张明、马利娅、潘家骅、薛蔚、黄翼然

陈子潇、甄帅、徐晓莉、周光胜、陈志攀、姜凯燕

### 许可证信息
本仓库中的代码采用GNU Affero General Public License发布。数据集则在“知识共享 署名-非商业性使用-相同方式共享 4.0 国际许可协议”（CC BY-NC-SA 4.0）下提供，这意味着您不能将数据集用于商业目的；如果您对数据集进行再混合、转换或基于数据集进行创作，您必须在相同的许可协议下分发您的贡献。