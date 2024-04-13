import os
import platform
import torch
from transformers import AutoTokenizer, AutoModel
from transformers import AutoModelForCausalLM
from transformers.generation.utils import GenerationConfig
import re
import argparse

Path_dicts = {'Huatuogpt-13B': "",
              'Baichuan2-7B-chat': "",
              'Baichuan2-13B-chat': "",
              'Baichuan-13B-chat': "",
              'Chatglm2-6b': "",
              'Chatglm3-6b': "",
              'Qwen-7B-Chat': "",
              'Qwen-14B-Chat': ""
              }


# multi-agent framework: baichuan2-13B
class MapAgent:
    def __init__(self, model_name, device=0):

        assert model_name in Path_dicts.keys(), "Not support current model!"

        self.model_name = model_name
        self.path = Path_dicts[self.model_name]
        self.model, self.tokenizer = self.load_model(self.path, device)
        self.eos = self.get_eos()

    def get_eos(self):
        return self.tokenizer.eos_token

    def load_model(self, path, device):
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

        if 'Chatglm' in self.model_name:

            model = AutoModel.from_pretrained(path, trust_remote_code=True, device=device)
        else:

            model = AutoModelForCausalLM.from_pretrained(path, trust_remote_code=True, device_map=device)
            model.generation_config = GenerationConfig.from_pretrained(path, trust_remote_code=True)

        model = model.eval()
        return model, tokenizer

    # 意图识别 mapping
    def rae_prompt(self, question):
        return f"""判断'{question}'的意图是否属于以下之一：[检查检验，症状，既往病史，手术史，用药史，婚育史，病理，月经史]，返回匹配到的意图。"""

    # 对话终止判断
    def final_prompt(self, question):
        return f"""判断'{question}'中是否包含一个询问或者一个问号。如果包含，返回是；如果不包含，返回不是。"""

    # 具体检查检验名称
    def test_prompt(self, category, question):
        return f"""判断'{question}'中是否包含检查检验的具体名称或具体名字（如'尿液常规检查'包含尿常规，'医学检查'不包含具体名字），返回是或者不是。"""

    # 意图识别 mapping 上层函数
    def mapping(self, question):
        prompt = self.rae_prompt(question)
        if 'Huatuo' in self.model_name or 'Baichuan' in self.model_name:
            messages = [{"role": "user", "content": prompt}]
            response = self.model.chat(self.tokenizer, messages)
        else:
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)
        return response

    # 对话终止判断 上层函数
    def is_finish(self, question):
        flag = False
        prompt = self.final_prompt(question)
        if 'Huatuo' in self.model_name or 'Baichuan' in self.model_name:
            messages = [{"role": "user", "content": prompt}]
            response = self.model.chat(self.tokenizer, messages)
        else:
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)

        # print(question)
        # print(response)
        if '不是' in response and ('？' not in question or '请告诉我' in question):
            # if '不是' in response:
            #     print('bushi')
            # if '？' not in question:
            #     print('不si')
            flag = True
        return flag

    # 具体检查检验名称 上层函数
    def has_name(self, category, question):
        prompt = self.test_prompt(category, question)
        if 'Huatuo' in self.model_name or 'Baichuan' in self.model_name:
            messages = [{"role": "user", "content": prompt}]
            response = self.model.chat(self.tokenizer, messages)
        else:
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)
        return response


# doctor
class MedAgent:
    def __init__(self, model_name, device=0):

        assert model_name in Path_dicts.keys(), "Not support current model!"

        self.model_name = model_name
        self.path = Path_dicts[self.model_name]
        self.model, self.tokenizer = self.load_model(self.path, device)
        self.eos = self.get_eos()

    def load_model(self, path, device):
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)

        if 'Chatglm' in self.model_name:
            model = AutoModel.from_pretrained(path, trust_remote_code=True, device=device)
        else:

            model = AutoModelForCausalLM.from_pretrained(path, trust_remote_code=True, device_map=device)
            model.generation_config = GenerationConfig.from_pretrained(path, trust_remote_code=True)
            

        model = model.eval()
        return model, tokenizer

    # QA场景
    def single_qa(self, question):
        prompt = self.single_prompt_format(question)
        if 'Huatuo' in self.model_name or 'Baichuan' in self.model_name:
            messages = [{"role": "user", "content": prompt}]
            response = self.model.chat(self.tokenizer, messages)
        else:
            print(self.model.generation_config)
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)
        return prompt, response

    # 推理场景，给定query，去问检查检验手段
    def single_reason(self, question):
        prompt = self.reason_prompt_format(question)
        if 'Huatuo' in self.model_name or 'Baichuan' in self.model_name:
            messages = [{"role": "user", "content": prompt}]
            response = self.model.chat(self.tokenizer, messages)
        else:
            response, _ = self.model.chat(self.tokenizer, prompt, history=None)
        return prompt, response

    # 多轮对话场景
    def multi_qa(self, question, history):
        if 'Huatuo' in self.model_name or 'Baichuan' in self.model_name:
            prompt = self.multi_prompt_format(question, history)
            messages = [{"role": "user", "content": prompt}]
            response = self.model.chat(self.tokenizer, messages)
            if history is None:
                history = []
            history += [(question, response)]
        elif 'Qwen' in self.model_name:
            
            prompt = question.strip()
            system_prompt = """你扮演医生的角色。在做出诊断前，每轮对话中你只能向病人询问一个问题，且必须属于下面的问题：
                               做过XXX检查吗？ 做过XXX检验吗？ 有XXX症状吗？ 既往病史有哪些？ 手术史是什么？ 最近的用药史是什么？ 婚育史？ 月经史？。
                               必须注意：你的回答和提问必须简洁（不能询问其他问题，不能对病人报告进行分析），最终诊断结果必须且只能包含具体疾病名称和治疗方案名称（不能建议进行其他检查）。"""

            response, history = self.model.chat(self.tokenizer, prompt, history=history, system=system_prompt)
        else:
            prompt = self.multi_prompt_format(question, history)
            response, history = self.model.chat(self.tokenizer, prompt, history=history)

        return response, history

    def get_eos(self):
        return self.tokenizer.eos_token

    # qa prompt 函数
    def single_prompt_format(self, query):
        if 'Huatuo' in self.model_name:
            return self.single_generate_prompt_huatuo(query)
        elif 'Baichuan' in self.model_name:
            return self.single_generate_prompt_baichuan(query)
        elif 'Chatglm' in self.model_name:
            return self.single_generate_prompt_chatglm(query)
        elif 'Qwen' in self.model_name:
            return self.single_generate_prompt_qwen(query)
        else:
            print("Not support current model!")
            return None

    # reason prompt 函数
    def reason_prompt_format(self, query):
        if 'Huatuo' in self.model_name:
            return self.reason_generate_prompt_huatuo(query)
        elif 'Baichuan' in self.model_name:
            return self.reason_generate_prompt_baichuan(query)
        elif 'Chatglm' in self.model_name:
            return self.reason_generate_prompt_chatglm(query)
        elif 'Qwen' in self.model_name:
            return self.reason_generate_prompt_qwen(query)
        else:
            print("Not support current model!")
            return None

    # multi-qa prompt 函数
    def multi_prompt_format(self, query, history):
        if 'Huatuo' in self.model_name:
            return self.multi_generate_prompt_huatuo(query, history)
        elif 'Baichuan' in self.model_name:
            return self.multi_generate_prompt_baichuan(query, history)
        elif 'Chatglm' in self.model_name:
            return self.multi_generate_prompt_chatglm(query, history)
        elif 'Qwen' in self.model_name:
            return self.multi_generate_prompt_qwen(query, history)
        else:
            print("Not support current model!")
            return None

    ######################################
    # single QA prompt
    ######################################
    def single_generate_prompt_huatuo(self, query):
        return f"""HuatuoGPT扮演医生的角色对病人进行疾病诊断和治疗建议，输出结果必须包含且只能包含最可能的疾病名称和最佳的治疗方案（手术、用药等），疾病、手术和药品等必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<HuatuoGPT>："""
    
    def single_generate_prompt_baichuan(self, query):
        return f"""你扮演医生的角色对病人进行疾病诊断和治疗建议，输出结果必须包含且只能包含可能性最大的疾病和最佳的治疗方案（手术、用药等），疾病、手术和药品等必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<医生>："""

    def single_generate_prompt_chatglm(self, query):
        return f"""你扮演医生的角色对病人进行疾病诊断和治疗建议，输出结果必须包含且只能包含可能性最大的疾病和最佳的治疗方案（手术、用药等），疾病、手术和药品等必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<医生>："""

    def single_generate_prompt_qwen(self, query):
        return f"""你扮演医生的角色对病人进行疾病诊断和治疗建议，输出结果必须包含且只能包含可能性最大的疾病和最佳的治疗方案（手术、用药等），疾病、手术和药品等必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<医生>："""

    ######################################
    # reason prompt
    ######################################
    def reason_generate_prompt_huatuo(self, query):
        return f"""HuatuoGPT对病人提出医学检查检验测试推荐，推荐结果必须包含且只能包含必须的检查测试名称（如上腹部增强CT、肾增强MR等），名称必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<HuatuoGPT>："""

    def reason_generate_prompt_baichuan(self, query):
        return f"""你扮演医生角色对病人提出医学检查检验测试推荐，推荐结果必须包含且只能包含必须的检查测试名称（如上腹部增强CT、肾增强MR等），名称必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<医生>："""

    def reason_generate_prompt_chatglm(self, query):
        return f"""你扮演医生角色对病人提出医学检查检验测试推荐，推荐结果必须包含且只能包含必须的检查测试名称（如上腹部增强CT、肾增强MR等），名称必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<医生>："""

    def reason_generate_prompt_qwen(self, query):
        return f"""你扮演医生角色对病人提出医学检查检验测试推荐，推荐结果必须包含且只能包含必须的检查测试名称（如上腹部增强CT、肾增强MR等），名称必须是官方医学术语。请不要输出其他无关内容。\n<病人>：{query}\n<医生>："""

    ######################################
    # multi-qa prompt
    ######################################
    def rae_prompt(self, question):
        return f"""判断问题类别并返回，只能返回一个类别：\n类别选项：[检查检验，症状，既往病史，手术史，用药史，婚育史，病理，月经史，诊断结果，治疗建议]\n问题：{question}"""

    # for huatuo
    def multi_generate_prompt_huatuo(self, query, history):
        if history is None:
            return f"""HuatuoGPT扮演医生的角色和病人进行多轮对话问诊，必须且只能在反问病人做过的检查检验报告后才能做出诊断。请不要输出其他无关内容。<病人>：{query} <HuatuoGPT>："""
        else:
            prompt = 'HuatuoGPT扮演医生的角色和病人进行多轮对话问诊，必须且只能在反问病人做过的检查检验报告后才能做出诊断。请不要输出其他无关内容。'
            for i, (old_query, response) in enumerate(history):
                prompt += "<病人>：{} <HuatuoGPT>：{}".format(old_query, response) + self.eos
            prompt += "<病人>：{} <HuatuoGPT>：".format(query)
            return prompt

    # for baichuan
    def multi_generate_prompt_baichuan(self, query, history):
        if history is None:
            return f"""扮演医生的角色和病人进行多轮对话问诊，必须且只能在反问病人做过的检查检验报告后才能给出诊断结果和治疗方案。请不要输出其他无关内容。\n<病人>：{query} <医生>："""
        else:
            prompt = '扮演医生的角色和病人进行多轮对话问诊，必须且只能在反问病人做过的检查检验报告后才能给出诊断结果和治疗方案。请不要输出其他无关内容。\n'
            for i, (old_query, response) in enumerate(history):
                prompt += "<病人>：{} <医生>：{}".format(old_query, response) + self.eos
            prompt += "<病人>：{} <医生>：".format(query)
            return prompt

    # for chatglm
    def multi_generate_prompt_chatglm(self, query, history):
        if history is None:
            return f"""你扮演医生的角色。在做出诊断前，每轮对话中你只能向病人询问一个问题，且必须属于下面的问题（某某是具体名称）：
                       做过某某检查吗？ 做过某某检验吗？ 有某某症状吗？ 既往病史有哪些？ 手术史是什么？ 最近的用药史是什么？ 婚育史？ 月经史？
                       必须注意：你的回答和提问必须简洁（不能询问其他问题，不能对病人报告进行分析），最终诊断结果必须且只能包含具体疾病名称和治疗方案名称（不能建议进行其他检查）。
                       <病人>：{query}
                       <医生>："""
        else:
            return '<病人>：' + query

    # for qwen
    def multi_generate_prompt_qwen(self, query, history):
        
        return query


        