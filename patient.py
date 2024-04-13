import pandas as pd
import os
import re

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

class StandardPatient:
    def __init__(self, xls_path):
        self.path = xls_path
        self.file_name = xls_path.split('/')[-1]
        self.subjects, self.items, self.results, self.limits, self.notes, self.hypernyms, self.score_cls = self.read_file()
        self.retrieval_keys = {}

        self.person_infor = self.read_person_infor()
        self.diagnosis_result = self.read_diagnosis_infor()
        self.diagnosis_factor = self.read_diagnosis_factor()
        self.treat_result = self.read_treat_infor()
        self.treat_factor = self.read_treat_factor()

        self.patient_infor = [self.person_infor, self.diagnosis_result, self.diagnosis_factor, self.treat_result, self.treat_factor]
        
        
    # {'首发问题': context, '患者意图':context}
    def read_person_infor(self):
        person_infor = {}
        for subject, result, note in zip(self.subjects, self.results, self.notes):
            if subject == '确诊疾病的反问的关键要素和正确顺序':
                break
            if subject == '诊断':
                continue
            else:
                person_infor[subject] = {'result': result, 'note': note, 'score': -1}
        return person_infor


    # {'左肾肿瘤、肾癌、肾占位': 左肾肿瘤、肾癌、肾占位, '双肾小囊肿':双肾小囊肿}
    def read_diagnosis_infor(self):
        diagnosis_infor = {}
        diag_result = []
        limit_words = ['诊断']
        for subject, result, note in zip(self.subjects, self.results, self.notes):
            if subject in limit_words:
                diag_result.append({'result': result, 'note': note, 'score': -1})
                diagnosis_infor[subject] = diag_result
        return diagnosis_infor
    
    


    # {'检查': [{'B超':{result:, note:, score:}}, {'CT': {result:, note:, score:}}]}
    def read_diagnosis_factor(self):
        diagnosis_factor = {}
 
        idx_begin = self.subjects.index('确诊疾病的反问的关键要素和正确顺序') + 1
        idx_end = self.subjects.index('正确顺序') + 1 

        symptom_result = []
        test_result = [] # 检查
        exam_result = [] # 检验
        pathology_result = []
        history_operation = []
        check_body = []
        
        for subject, item, result, limit, note in zip(self.subjects[idx_begin:idx_end], self.items[idx_begin:idx_end], self.results[idx_begin:idx_end], self.limits[idx_begin:idx_end], self.notes[idx_begin:idx_end]):
            if subject == '症状':
                if item != '无':
                    if result!='' and result=='无':
                        symptom_content = {item:
                                {'result':limit + result + item, 'note': note, 'score':-1}
                        }
                    else:
                        if result!='':
                            result = ' ' +result
                        symptom_content = {item:
                                {'result':limit + item + result, 'note': note, 'score':-1}
                        }
                    symptom_result.append(symptom_content)  
                else:
                    symptom_content = {'无症状':
                               {'result':'没有明显症状。', 'note': note, 'score':-1}
                    }
                    symptom_result.append(symptom_content)
                diagnosis_factor[subject]=symptom_result

            elif subject == '检查':
                out_item = item.split('、')[0] + '检查'
                if result!='':
                        result = '：' +result
                
                test_data = {item:
                    {'result': limit + out_item + result, 'note':note, 'score': -1}
                }
                test_result.append(test_data)
                diagnosis_factor[subject]=test_result

            elif subject == '查体':
                out_item = item.split('、')[0]
                if result!='':
                        result = ' ' +result
                if limit!='':
                    limit = limit + ' '

                test_data = {item:
                    {'result': limit + out_item + result, 'note':note, 'score': -1}
                }
                check_body.append(test_data)
                diagnosis_factor[subject]=check_body

            elif subject == '检验':
                out_item = item.split('、')[0]+'检验'
                if result!='':
                        result = ' ' +result
                
                test_data = {item:
                    {'result':limit + out_item + result, 'note':note, 'score': -1}
                }
                exam_result.append(test_data)
                diagnosis_factor[subject]=exam_result

            elif subject == '病理':
                out_item = item.split('、')[0]
                if result!='':
                        result = ' ' +result
                if limit!='':
                    limit = ' ' + limit
                pathology_data = {item:
                    {'result':out_item + result + limit, 'note':note, 'score': -1}
                }
                pathology_result.append(pathology_data)
                diagnosis_factor[subject]=pathology_result
            
            elif subject == '手术史':
                if result!='':
                        result = ' ' +result
                if limit!='':
                    limit = ' ' + limit

                operation = {item:
                                {'result':item + result + limit, 'note': note, 'score':-1}
                                }
                history_operation.append(operation)
                diagnosis_factor[subject]= history_operation
            
            elif subject == '正确顺序':
                item = '正确顺序'
                result = {'result':result, 'score': 0}

        return diagnosis_factor
    
    

    # {'治疗': [肾部分切除]}
    def read_treat_infor(self):
        treat_infor = {}
        treat_result = []
        limit_words = ['治疗']
        for subject, result, limit, note in zip(self.subjects, self.results, self.limits, self.notes):
            if subject in limit_words:
                treat_result.append({'result': result, 'note': note, 'score': -1})
                treat_infor[subject] = treat_result

        return treat_infor
    

    # {'红细胞沉降率(ESR)、血沉, 术前检查、术前验血、术前化验': 入院一天后，红细胞沉降率ESR 5mm/h.}
    def read_treat_factor(self):
        treat_factor = {}
        if '治疗方案的关键要素' not in self.subjects:
            return treat_factor
        idx_begin = self.subjects.index('治疗方案的关键要素') + 1

        history_operation = []
        history_drug = []
        general_case = []
        history_disease = []
        test_pre_operation = []
        exam_pre_operation = []
        exam = []
       
        for subject, item, result, limit, hypernym, note in zip(self.subjects[idx_begin:], self.items[idx_begin:], self.results[idx_begin:], self.limits[idx_begin:], self.hypernyms[idx_begin:], self.notes[idx_begin:]):

            if subject == '手术史':
                if item == '无':
                    operation = {'手术史':
                                  {'result':'没有做过其他手术。', 'note': note, 'score':-1}
                                 }
                    history_operation.append(operation)
                    treat_factor[subject]= history_operation
                else:
                    if result!='':
                        result = '，' +result
                    if limit!='':
                        limit = '，' + limit

                    operation = {item:
                                  {'result':item + result + limit, 'note': note, 'score':-1}
                                 }
                    history_operation.append(operation)
                    treat_factor[subject]= history_operation
            
            elif subject == '用药史':
                if item == '无':
                    drug = {'用药史':
                                  {'result':'没有相关用药史。', 'note': note, 'score':-1}
                                 }
                    history_drug.append(drug)
                    treat_factor[subject]= history_drug
                else:
                    if result!='':
                        result = '，' +result
                    if limit!='':
                        limit = '，' + limit

                    drug = {item:
                                  {'result':item + result + limit, 'note': note, 'score':-1}
                                 }
                    history_drug.append(drug)
                    treat_factor[subject]= history_drug

            elif subject == '一般情况':
                if result == '无':
                    general = {'一般情况':
                                  {'result':'没有其他常见的一般情况。', 'note': note, 'score':-1}
                                 }
                    general_case.append(general)
                    treat_factor[subject]= general_case
                else:
                    general = {subject:
                                  {'result':'一般情况：' + result, 'note': note, 'score':-1}
                                 }
                    general_case.append(general)
                    treat_factor[subject]= general_case

            elif subject == '既往史' or subject == '既往病史':
                subject = '既往病史'
                out_item = item.split('、')[0]
                
                if item == '无':
                    disease = {subject:
                                  {'result':'我没有既往病史。', 'note': note, 'score':-1}
                                 }
                    history_disease.append(disease)
                    treat_factor[subject]= history_disease
                else:
                    if result!='':
                        result = '，' +result
                    if limit!='':
                        limit = '，' + limit
                    disease = {item:
                                  {'result': out_item  + limit + result, 'note': note, 'score':-1}
                                }
                    history_disease.append(disease)
                    treat_factor[subject]= history_disease

            elif subject == '婚育史' or subject == '月经史':
                history_marry = {subject:
                                  {'result': item + result, 'note': note, 'score':-1}
                        }

                treat_factor[subject] = [history_marry]

            elif subject == '检验':
                out_item = item.split('、')[0]
                if result!='':
                        result = '，' +result
                if limit!='':
                    limit = '，' + limit

                test_operation = {item:
                    {'result':out_item  + result + limit, 'note': note, 'score':-1}
                }
                test_pre_operation.append(test_operation)

                treat_factor[subject]= test_pre_operation
            
            elif subject == '检查':
                out_item = item.split('、')[0]
                if result!='':
                        result = '，' +result
                if limit!='':
                    limit = '，' + limit

                test_operation = {item:
                    {'result':out_item  + result + limit, 'note': note, 'score':-1}
                }
                exam_pre_operation.append(test_operation)

                treat_factor[subject]= exam_pre_operation

        return treat_factor

        
    def read_file(self):
        data = pd.read_excel(self.path)
        data = data.fillna('')
        subjects = data['类目大项'].values.tolist()
        idx_end = len(subjects)
        if '合并' in subjects:
            idx_end = subjects.index('合并')
        
        subjects = subjects[:idx_end]
        items = data['类目子项'].values.tolist()[:idx_end]
        results = data['结果'].values.tolist()[:idx_end]
        limits = data['约束'].values.tolist()[:idx_end]
        notes = data['备注'].values.tolist()[:idx_end]
        hypernyms = data['上位词'].values.tolist()[:idx_end]
        score_cls = data['得分项分类'].values.tolist()[:idx_end]
        return subjects, items, results, limits, notes, hypernyms, score_cls


    def query_info(self, query): #通过字典key进行匹配
        # 检索结果
        result = []
        if query == '检查':
            return ['医生你问的是哪个检查？']
        
        for sub_infor in self.patient_infor:
            keys = sub_infor.keys()
            for key in keys: #类目子项，上位词
                key_list = key.split('，') # [类目子项,上位词]
                
                for idx, sub_key in enumerate(key_list):
                    sub_key_list = sub_key.split('、') #[同义词,同义词]
                    for sub_key in sub_key_list:
                        if query.lower()==sub_key.lower():
                            sub_result = sub_infor[key]['result']
                            if sub_infor[key]['note']=='重要得分项':
                                sub_infor[key]['score']=2
                            elif sub_infor[key]['note']=='得分项':
                                sub_infor[key]['score']=1
                            
                            result.append(sub_result)
                            if idx == 0:
                                return result
                            break

        return result

    def print_info(self):
        print(self.person_infor)
        print(self.diagnosis_result)
        print(self.diagnosis_factor)
        print(self.treat_result)
        print(self.treat_factor)

    def calculate_score(self):
        all_score = 0
        real_score = 0
        acc_question_count = 0
        all_question_count = 0

        for _, sub_results in self.diagnosis_factor.items():
            for sub_result in sub_results:
                for _, item_dict in sub_result.items():
                    if item_dict['note'] == '得分项':
                        all_score += 1
                    elif item_dict['note'] == '重要得分项':
                        all_score += 2

                        all_question_count += 1
                        if item_dict['score'] == 2:
                            acc_question_count += 1

                    else:
                        pass
                    if item_dict['score'] != -1:
                        real_score += item_dict['score']

        for _, sub_results in self.treat_factor.items():
            for sub_result in sub_results:
                for _, item_dict in sub_result.items():
                    if item_dict['note'] == '得分项':
                        all_score += 1
                    elif item_dict['note'] == '重要得分项':
                        all_score += 2
                    else:
                        pass
                    if item_dict['score'] != -1:
                        real_score += item_dict['score']

        return all_score, real_score, acc_question_count, all_question_count

    def query_aim(self):
        return self.person_infor['首发问题']['result']

    def query_max_round(self):
        max_round = self.person_infor['预计轮次']['result']

        max_round = re.sub(u"([^\u0030-\u0039])", "", max_round)
        # max_round = max_round.replace('轮', '')
        return int(max_round)
    
    def query_disease(self):
        result = []
        
        for sub_result in self.diagnosis_result['诊断']:
            result.append(sub_result['result'])

        result = '；'.join(result)
        return result

    def query_treat(self):
        result = []
        for sub_result in self.treat_result['治疗']:
            result.append(sub_result['result'])
        result = '；'.join(result)
        return result
    
    def query_test_qa(self):
        result = []
        
        limit_words = ['症状','检查', '检验', '查体']
        
        for sub_item in limit_words:
            if sub_item in self.diagnosis_factor:
                result.append(sub_item + '如下：') 
                for result_idx, sub_result in enumerate(self.diagnosis_factor[sub_item]):
                    for key, value_dict in sub_result.items():
                        self.diagnosis_factor[sub_item][result_idx][key]['score']=0
                        result.append(value_dict['result'])
                        break
                    

        result = '\n'.join(result)
        return result

    
    def query_test_multiqa(self, limit_words):
        result = []
        for sub_item in limit_words:
            if sub_item in self.diagnosis_factor:
                for result_idx, sub_result in enumerate(self.diagnosis_factor[sub_item]):
                    for key, value_dict in sub_result.items():
                        # print(value_dict)
                        if value_dict['score']==-1:
                            self.diagnosis_factor[sub_item][result_idx][key]['score']=0
                            return [value_dict['result']]       
        return result

    def query_reason_test(self):
        test = []
        symptom = []
        
        if '症状' in self.diagnosis_factor:
            symptom.append('症状如下：') 
            for sub_result in self.diagnosis_factor['症状']:
                symptom.append(list(sub_result.values())[0]['result'])

        limit_words = ['检查', '检验', '查体']
        for sub_item in limit_words:
            if sub_item in self.diagnosis_factor:
                for sub_result in self.diagnosis_factor[sub_item]:
                    test.append(list(sub_result.keys())[0].split('、')[0])

            if sub_item in self.treat_factor:
                for sub_result in self.treat_factor[sub_item]:
                    test.append(list(sub_result.keys())[0].split('、')[0])
        
        symptom = '\n'.join(symptom)
        
        return symptom, test
    
    def get_question(self):
        aim = self.query_aim()
        test = self.query_test_qa()
        disease = self.query_disease()
        treat = self.query_treat()
        
        return test, disease, treat

    def get_question_zero(self):
        aim = self.query_aim()
        test = self.query_test_qa()
        disease = self.query_disease()
        treat = self.query_treat()
        
        return aim, disease, treat

    def get_reason_question(self):
        aim = self.query_aim()
        symptom, test = self.query_reason_test()

        return aim + symptom, test
    

    def get_format_disease_treat(self):
        diagnosis_result = []
        for sub_diagnosis_result in self.diagnosis_result['诊断']:
            # print(sub_diagnosis_result)
            diagnosis_result.append(sub_diagnosis_result['result'])
        # diagnosis_result = '、'.join(diagnosis_result)
        diagnosis_result = diagnosis_result[0]

        treat_result = []
        for sub_treat_result in self.treat_result['治疗']:
            treat_result.append(sub_treat_result['result'])
        # treat_result = '、'.join(treat_result)
        treat_result = treat_result[0]
       
        return self.file_name, diagnosis_result, treat_result

    def category_2_item(self, category, doc_word, test_syn_table):
        doc_word = doc_word.lower()
        response = []
        if category in list(self.diagnosis_factor.keys()):
            result_list = self.diagnosis_factor[category] # 取到大类数据

            for result_idx, sub_result in enumerate(result_list): # 遍历到大类的子类
                is_syn = False
                key_word = list(sub_result.keys())[0]
                key_word = key_word.split('、')[0].lower()

                retrieval_syn = [key_word]
                # 寻找子类的同义词表
                for sub_eval_test in test_syn_table:#遍历同义词表每一行
                    for sub_eval_test_item in sub_eval_test:#遍历一行中的每一个同义词
                        if sub_eval_test_item in key_word:#判断同义词是否命中
                            retrieval_syn = sub_eval_test #同义词命中
                        
                            is_syn = True
                            break
                    
                    if is_syn is True:
                        break
                
                
                # 判断子类是否在问题中出现
                for syn_item in retrieval_syn:
                    if syn_item in doc_word:
                        for key_dict, value_dict in sub_result.items():
                            if value_dict['score']!=-1:
                                return ['您已经问过这个问题，请询问我其他' + category +'信息。']
                            else:
                                response.append(value_dict['result'])
                                if value_dict['note']=='得分项':
                                    self.diagnosis_factor[category][result_idx][key_dict]['score']=1
                                elif value_dict['note']=='重要得分项':
                                    self.diagnosis_factor[category][result_idx][key_dict]['score']=2
                            break
                        break
                
                
                
        if category in list(self.treat_factor.keys()):
            result_list = self.treat_factor[category] # 检索到大类
            
            for result_idx, sub_result in enumerate(result_list): # 遍历到大类的子类
                is_syn = False
                key_word = list(sub_result.keys())[0]
                key_word = key_word.split('、')[0].lower()

                retrieval_syn = [key_word]
                # 检索同义词表
                for sub_eval_test in test_syn_table:#遍历同义词表每一行
                    for sub_eval_test_item in sub_eval_test:#遍历一行中的每一个同义词
                        if sub_eval_test_item in key_word:#判断同义词是否命中
                            retrieval_syn = sub_eval_test
                            is_syn = True
                            break
                    
                    if is_syn is True:
                        break
                    
                for syn_item in retrieval_syn:
                    if syn_item in doc_word:
                        for key_dict, value_dict in sub_result.items():
                            if value_dict['score']!=-1:
                                return ['您已经问过这个问题，请询问我其他' + category +'信息。']
                            else:
                                response.append(value_dict['result'])
                                if value_dict['note']=='得分项':
                                    self.treat_factor[category][result_idx][key_dict]['score']=1
                                elif value_dict['note']=='重要得分项':
                                    self.treat_factor[category][result_idx][key_dict]['score']=2
                            break
                        break
                    
        return response

    def retrieval_direct(self, category, doc_word, test_syn_table):
        direct_results = []
        if category in list(self.diagnosis_factor.keys()):
            for sub_result in self.diagnosis_factor[category]:
                direct_results.append(list(sub_result.values())[0]['result']) 
            
        if category in list(self.treat_factor.keys()):
            for sub_result in self.treat_factor[category]:
                direct_results.append(list(sub_result.values())[0]['result']) 
        
        if len(direct_results) == 0:
            direct_results = ['我没有' + category + '的相关信息。']
        
        return '。'.join(direct_results)

    def retrieval_second(self, category, doc_word, test_syn_table):
        response = self.category_2_item(category, doc_word, test_syn_table)
        if len(response) == 0:
            second_back_response = []
            if category in list(self.diagnosis_factor.keys()):
                result_list = self.diagnosis_factor[category]
                for sub_idx, sub_result in enumerate(result_list):
                    for key_dict, value_dict in sub_result.items():
                        if value_dict['score']==-1:
                            second_back_response.append(value_dict['result'])
                            self.diagnosis_factor[category][sub_idx][key_dict]['score']=1
                            break
                    if len(second_back_response)!=0:
                        break
                
            if category in list(self.treat_factor.keys()):
                result_list = self.treat_factor[category]
                for sub_idx, sub_result in enumerate(result_list):
                    for key_dict, value_dict in sub_result.items():
                        if value_dict['score']==-1:
                            second_back_response.append(value_dict['result'])
                            self.treat_factor[category][sub_idx][key_dict]['score']=1
                            break
                    if len(second_back_response)!=0:
                        break

            if len(second_back_response) == 0:
                response = ['我没有您问到的' + category + '信息。']
            else:
                response = second_back_response

        return ' '.join(response)

    def retrieval_full(self, category, doc_word, test_syn_table, sub_name):
        if category == '检查检验':
            response_test = self.category_2_item('检查', doc_word, test_syn_table)
            response_exam = self.category_2_item('检验', doc_word, test_syn_table)
            response_disea = self.category_2_item('病理', doc_word, test_syn_table)
            response = response_test + response_exam + response_disea
            print(response)
        else:
            response = self.category_2_item(category, doc_word, test_syn_table)

        if len(response) == 0:
            if category == '检查检验':
                response = self.query_test_multiqa(['检查', '检验', '病理'])
                
            else:
                response = self.query_test_multiqa([category])

            if len(response)==0:
                return '我没有' + category + '相关信息。'
            else:
                response = '我没有做过这个检查。但我有以下检查报告：\n' + '\n'.join(response)
                return response
        else:
            return '\n'.join(response)

                
def get_files_in_directory(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file[-4:]!='xlsx':
                continue
            
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    return file_list


def get_result():
    # test case
    base_path = '../data'

    file_list = get_files_in_directory(base_path)


    file_names = []
    disease_names = []
    treat_names = []
    same_meaning = []

    for file_item in file_list:
        print(file_item)
        if file_item[-4:]!='xlsx':
            continue
        
        # file_item = file_item.decode('utf-8')
        file_item = os.path.realpath(file_item)
        
        patient = StandardPatient(file_item)
        
        file_name, diagnosis_result, treat_result = patient.get_format_disease_treat()
        
        file_names.append(file_name)
        disease_names.append(diagnosis_result)
        treat_names.append(treat_result)
        same_meaning.append('')

        # 创建一个数据框
    data = {'数据文件名称': file_names,
            '疾病名称': disease_names,
            '疾病同义词':same_meaning,
            '治疗方案名称':treat_names,
            '治疗方案同义词':same_meaning}
    df = pd.DataFrame(data)
    # 保存数据框为 xlsx 文件
    df.to_excel('疾病同义词表.xlsx', index=False)

if __name__ == '__main__':
    test_syn_table = query_test_syn()
    
    # for test case
    file_item = 'test_case.xlsx'
    
    file_item = os.path.realpath(file_item)
        
    patient = StandardPatient(file_item)

    disease = patient.retrieval_full('检查检验', '好，对于你的情况我表示关心。你能告诉我做了哪些检查，以及检查结果吗？比如膀胱超声，尿液常规，尿液细胞学检查等。', test_syn_table, '')
    print(disease)
       
        
