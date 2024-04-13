from patient import StandardPatient, get_files_in_directory
from agent import MedAgent,Path_dicts, MapAgent
import os
import pandas as pd

def diag_judge(person_file, answer, eval_file_name, eval_treat_data, eval_diag_data):
    diag_result = 0
    treat_result = 0
    idx_mapping = []
    map_idx = eval_file_name.index(person_file)

    answer = answer.lower()
    eval_treat_list = eval_treat_data[map_idx].split('、')
    for eval_treat_item in eval_treat_list:
        if eval_treat_item in answer:
            treat_result = 1
            break

    eval_diag_list = eval_diag_data[map_idx].split('、')
    for eval_diag_item in eval_diag_list:
        if eval_diag_item in answer:
            diag_result = 1
            break
    
    return diag_result, treat_result

def diag_syn():
    # load diagnosis words for evaluation
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

    return eval_file_name, eval_diag_data, eval_treat_data

def query_test_syn():
    # load test syn words for evaluation
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
    
    return eval_test

#疾病、治疗同义词
eval_file_name, eval_diag_data, eval_treat_data = diag_syn()


#建模病人
base_path = '../data'
patients=[]
file_list = get_files_in_directory(base_path)

for file_item in file_list:
    print(file_item)
    if file_item[-4:]!='xlsx':
        continue
    file_item = os.path.realpath(file_item)
    patients.append(StandardPatient(file_item))


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


# 定义Query-Key Agent for RAE
PatientAgent = MapAgent(model_names[2], device=0)

# 定义Doctor
DoctorAgent = MedAgent(model_names[5], device=1)


# 检查同义词表 二级映射
test_syn_table = query_test_syn()

# 项目大类 一级映射
category_list = ['检查检验','症状','既往病史','手术史','用药史','婚育史','月经史','诊断结果','治疗建议']
direct_item = ['婚育史','月经史']
second_item = ['症状', '既往病史', '手术史', '用药史']
full_item = ['检查检验']

# 信息完整性
all_score = 0 #总的分数
real_score = 0 #获得的分数

# 诊断逻辑性，诊断治疗的准确性
diagnosis_count = 0
treat_count = 0

# 人文实用性
over_round_count = 0 #超过推荐的病人数
all_round = 0 #总的推荐轮数
real_round = 0 #推荐轮数以内的轮数

# 合理性，精准提问重要得分项
all_question_count = 0
acc_question_count = 0

with open('multi_qa_gpt4.txt',"w", encoding='utf-8') as result_file:
    
    for person_idx, Patient in enumerate(patients):
        print('病人ID：', person_idx)
        cache = ''
        end_flag = False
        patient_word = Patient.query_aim()
       
        all_round += Patient.query_max_round()
        max_round = 20
        count_round = 0
        history = None
        
        while True:
            #轮次计数
            count_round += 1

            doc_word, history = DoctorAgent.multi_qa(patient_word, history) #医生反问或者诊断
            
            #打印对话
            print('患者：{}'.format(patient_word))
            print('医生：{}'.format(doc_word))

            cache = cache + '患者：' + patient_word + '\n' + '医生：' + doc_word + '\n'

            is_finish = PatientAgent.is_finish(doc_word)  #结束对话映射
            # print('结束对话', is_finish)
            if is_finish is not True:
                category_result = []
                category = PatientAgent.mapping(doc_word)  #query-key映射
                # print('分类', category)

                for sub_category in category_list:
                    if sub_category in category:
                        category_result.append(sub_category)
               
                # 条件过滤
                if len(category_result)==0:
                    # 无关键信息
                    patient_word = '我不知道，请医生询问其他问题！'
                # SPs检索答案
                else:
                    rae_patient_words = []
                    for category_item in category_result:
                        if category_item in direct_item:
                            rae_patient_word = Patient.retrieval_direct(category_item, doc_word, test_syn_table)  #key-value映射
                            rae_patient_words.append(rae_patient_word)
                        elif category_item in second_item:
                            rae_patient_word = Patient.retrieval_second(category_item, doc_word, test_syn_table)  #key-value映射
                            rae_patient_words.append(rae_patient_word)
                        else:
                            print(category_item)
                            has_name = PatientAgent.has_name(category_item, doc_word)
                            print('has_name', has_name)
                            if '不是' in has_name:
                                sub_name = False
                            else:
                                sub_name = True
                            
                            rae_patient_word = Patient.retrieval_full(category_item, doc_word, test_syn_table, sub_name)  #key-value映射
                            rae_patient_words.append(rae_patient_word)
                    patient_word = '\n'.join(rae_patient_words)
            else:
                patient_word = '谢谢医生！'
                real_round += count_round
                end_flag = True

            

            if count_round > max_round:
                over_round_count += 1
                end_flag = True

            if end_flag:
                person_all_score, person_real_score, person_acc_question_count, person_all_question_count = Patient.calculate_score()
                diag_result, treat_result = diag_judge(Patient.file_name, doc_word, eval_file_name, eval_treat_data, eval_diag_data)
                
                # 信息完整性
                all_score += person_all_score #总的分数
                real_score += person_real_score #获得的分数

                # 诊断逻辑性，诊断治疗的准确性
                diagnosis_count += diag_result
                treat_count += treat_result

                # 合理性，精准提问
                all_question_count += person_all_question_count
                acc_question_count += person_acc_question_count

                
                break
        cache = cache + '\n\n\n\n'
        result_file.write(cache)

    cache = f"""
            # 信息完整性
            all_score = {all_score} #总的分数
            real_score = {real_score} #获得的分数

            # 诊断逻辑性，诊断治疗的准确性
            diagnosis_count = {diagnosis_count}
            treat_count = {treat_count}

            # 人文实用性
            over_round_count = {over_round_count} #超过推荐的病人数
            all_round = {all_round} #总的推荐轮数
            real_round = {real_round} #推荐轮数以内的轮数

            # 合理性，精准提问重要得分项
            all_question_count = {all_question_count}
            acc_question_count = {acc_question_count}
            """
    result_file.write(cache)
result_file.close()


    
            