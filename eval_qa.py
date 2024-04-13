from patient import StandardPatient, get_files_in_directory
from agent import MedAgent,Path_dicts
import os
import pandas as pd

# load words for evaluation
eval_data = pd.read_excel('diag_table.xlsx')
eval_data = eval_data.fillna('')
file_name = eval_data['数据文件名称'].values.tolist()  
diag_name = eval_data['疾病名称'].values.tolist()
diag_synonym = eval_data['同义词'].values.tolist()
treat_name = eval_data['治疗方案名称'].values.tolist()
treat_synonym = eval_data['治疗方案同义词'].values.tolist()

eval_file_name = []
eval_diag_data = []
eval_treat_data = []

for idx, file_item in enumerate(file_name):
    if file_item == '':
        diag = diag_name[idx]
        diag_syn = diag_synonym[idx]
        treat = treat_name[idx]
        treat_syn = treat_synonym[idx]

        if diag!='':
            eval_diag_data[-1] = eval_diag_data[-1] + '、' + diag
        if diag_syn!='':
            eval_diag_data[-1] = eval_diag_data[-1] + '、' + diag_syn
        if treat!='':
            eval_treat_data[-1] = eval_treat_data[-1] + '、' + treat
        if treat_syn!='':
            eval_treat_data[-1] = eval_treat_data[-1] + '、' + treat_syn

    else:
        eval_file_name.append(file_item)
        diag = diag_name[idx]
        diag_syn = diag_synonym[idx]
        treat = treat_name[idx]
        treat_syn = treat_synonym[idx]

        if diag_syn!='':
            diag = diag + '、' + diag_syn
        if treat_syn!= '':
            treat = treat + '、' + treat_syn

        eval_diag_data.append(diag)
        eval_treat_data.append(treat)

# 大小写不敏感操作，都是用小写.lower():
eval_diag_data = [item.lower() for item in eval_diag_data]  
eval_treat_data = [item.lower() for item in eval_treat_data]  

if len(eval_diag_data) != len(eval_treat_data):
    print("There is an error.")


base_path = 'benchmark_data'
patients=[]
file_list = get_files_in_directory(base_path)

for file_item in file_list:
    print(file_item)
    if file_item[-4:]!='xlsx':
        continue
    file_item = os.path.realpath(file_item)
    patients.append(StandardPatient(file_item))

# eval param
overall_count = len(eval_diag_data)
diag_score = 0
treat_score = 0



#0: huatuo-13B
#1: baichuan2-7B
#2: baichuan2-13B
#3: baichuan-13B
#4: Chatglm2-6B
#5: Chatglm3-6B
#6: qwen-7B
#7: qwen-14B

model_names = list(Path_dicts.keys())
print(model_names)

model_name = model_names[7]
print(model_name)
Doctor = MedAgent(model_name)

file_name = 'result.txt'
with open(file_name,"w", encoding='utf-8') as result_file:
    for Patient in patients:
        
        person_file = Patient.file_name
        print(person_file)
        
        map_idx = eval_file_name.index(person_file)

        query, diease, treat = Patient.get_question()  
        prompt, answer = Doctor.single_qa(query)

        answer = answer.lower()
        eval_treat_list = eval_treat_data[map_idx].split('、')
        for eval_treat_item in eval_treat_list:
            if eval_treat_item in answer:
                treat_score += 1
                break

        eval_diag_list = eval_diag_data[map_idx].split('、')
        for eval_diag_item in eval_diag_list:
            if eval_diag_item in answer:
                diag_score += 1
                break

        cache = prompt + answer + '\r\n' + '答案：' + diease + '，' + treat + '\r\n\r\n\r\n'
            
        result_file.write(cache)
    result_file.close()
            

print(diag_score)
print(treat_score)
print(overall_count)
