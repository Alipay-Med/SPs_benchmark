from patient import StandardPatient, get_files_in_directory
from agent import MedAgent,Path_dicts
import os
import pandas as pd

# load words for evaluation
eval_data = pd.read_excel('word_table.xlsx')
eval_data = eval_data.fillna('')
test_name = eval_data['名称'].values.tolist()  
test_hypernym = eval_data['上位词'].values.tolist()
test_synonym = eval_data['同义词'].values.tolist()

eval_test = []
for test_item, hypernym_item, syn_item in zip(test_name,test_hypernym,test_synonym):
    result = ''
    if test_item!='':
        result += test_item
    if hypernym_item!='':
        result = result + '、' + hypernym_item
    if syn_item!='':
        result = result + '、' +  syn_item

    if result=='':
        continue
    result = result.lower()
    eval_test.append(result.split('、'))
    

base_path = 'benchmark_data'
patients=[]
file_list = get_files_in_directory(base_path)
for file_item in file_list:
    print(file_item)
    if file_item[-4:]!='xlsx':
        continue
    file_item = os.path.realpath(file_item)
    
    patients.append(StandardPatient(file_item))

 


# print(eval_test)

#0: huatuo-13B
#1: baichuan2-7B
#2: baichuan2-13B
#3: baichuan-13B
#4: Chatglm2-6B
#5: Chatglm3-6B
#6: qwen-7B
#7: qwen-14B

#设置模型
model_names = list(Path_dicts.keys())
print(model_names)
model_name = model_names[0]
Doctor = MedAgent(model_name)


file_name = 'result.txt'

score = 0
count = 0

with open(file_name,"w", encoding='utf-8') as result_file:
    for Patient in patients:
        query, test = Patient.get_reason_question()
        prompt, answer = Doctor.single_reason(query)
        answer = answer.lower()

        test = list(set(test))
        count += len(test)
        
        for sub_test in list(set(test)):
            match_flag = False
            for sub_eval_test in eval_test:
                for sub_eval_test_item in sub_eval_test:
                    if sub_eval_test_item in sub_test:
                        for sub_eval_test_item in sub_eval_test:
                            if sub_eval_test_item in answer:
                                score+=1
                                match_flag = True
                                break
                    if match_flag is True:
                        break
                if match_flag is True:
                    break

        cache = answer + '\r\n\r\n\r\n'
            
        result_file.write(cache)
    result_file.close()

    
                    

print(score)
print(count)
