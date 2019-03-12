# -*- coding: utf-8 -*-
'''
对name.txt文件进行分析
包括 常用字提取保存
    姓、名标记 S BE - 用于训练HMM的发射矩阵和转移矩阵, 专门用来对姓和名进行识别
'''
import codecs

def sign_for_hmm():
    with open("files/name.txt", 'r') as f:
        lines = f.readlines()

    emit_prob = {
        'B': {},
        'M': {},
        'E': {},
        'S': {}
    }
    words_num = {}
    for line in lines:
        if len(line) == 3:
            emit_prob['S'][line[0]] = emit_prob['S'].get(line[0], 0) + 1
            words_num[line[0]] = words_num.get(line[0], 0) + 1
            emit_prob['B'][line[1]] = emit_prob['B'].get(line[1], 0) + 1
            words_num[line[1]] = words_num.get(line[1], 0) + 1
            emit_prob['E'][line[2]] = emit_prob['E'].get(line[2], 0) + 1
            words_num[line[2]] = words_num.get(line[2], 0) + 1

'''
计算作为姓名的常用字
'''

def count():
    with codecs.open('files/name.txt', 'r', 'utf-8') as f:
        lines = f.read()
    lines = lines.split('\n')
    first_name = {}
    second_name = {}
    for line in lines:
        if len(line) == 3:
            first_name[line[0]] = first_name.get(line[0], 0) + 1
            second_name[line[1]] = second_name.get(line[1], 0) + 1
            second_name[line[2]] = second_name.get(line[2], 0) + 1
        elif len(line) == 4:
            first_name[line[:2]] = first_name.get(line[:2], 0) + 1
            second_name[line[2]] = second_name.get(line[2], 0) + 1
            second_name[line[3]] = second_name.get(line[3], 0) + 1

    first_name = sorted(first_name.items(), key=lambda x: x[1], reverse=True)
    second_name = sorted(second_name.items(), key=lambda x: x[1], reverse=True)

    with open('files/first_name.txt', 'w') as f:
        for s in first_name:
            try:
                f.write(s[0] + ' ' + str(s[1]) + '\n')
            except:
                pass
    with open('files/second_name.txt', 'w') as f:
        for s in second_name:
            try:
                f.write(s[0] + ' ' + str(s[1]) + '\n')
            except:
                pass

count()
