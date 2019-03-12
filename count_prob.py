# -*- coding: utf-8 -*-
'''
HMM Model
Compute π A B
init=
{
	'B':p,
	'M':p,
	'E':p,
	'S':p
}
transition={
	'B':{
		'B':p,
    	'M':p,
	}.
	...
}
emission={
	'B':{
	'word1':p,
	'word2':p,
	...
	},
	'M':{
	...
	}
	... 
} 
'''

from collections import defaultdict
import json
import math
import re
import codecs

'''
TODO: 平滑处理 
TODO: 使用更多数据训练？？？
'''
from config import *

class CountProb:

    def __init__(self, seg_file=BIDICFILE, dic_file=DICFILE):
        # 平滑
        self.inf = -3.14e+100
        # B M E S
        self.state = ['B', 'M', 'E', 'S']
        # 获取训练集
        self.seg_lists = self.analysis_seg_file(seg_file)
        self.dic = self.analysis_dic_file(dic_file)
        # 训练参数
        self.count_init_prob(self.seg_lists)
        self.count_trans_prob(self.seg_lists)
        self.count_emission_prob(self.dic)

    # 解析seg语料库,获取只有分词的单句
    def analysis_seg_file(self, seg_file):
        with codecs.open(seg_file, 'r', 'gbk') as f:
            text = f.read()
        lines = text.split('\r\n')
        seg_lists = []
        # 获得单个词
        for line in lines:
            # 正则匹配
            pattern = re.compile(r'^199801')
            # next line
            if not re.match(pattern, line):
                continue
            # match Word/sign including [Word/sign
            regex = r'\s[^\s^/]+/\w+'
            segs = re.findall(regex, line)
            # 提取分词
            seg_list = []
            for seg in segs:
                # remove the [ that maybe exists, and then remove the space at
                # the begining
                s = seg.replace('[', '')[1:]
                word = s.split('/')[0]
                # all the segmentation words in the line
                seg_list.append(word)
            seg_lists.append(seg_list)
        return seg_lists

    # 读取词频文件dic(word, frequence) by reading from the dic file
    def analysis_dic_file(self, dic_file):
        with codecs.open(dic_file, 'r', 'gbk') as f:
            text = f.read()
        lines = text.split('\r\n')
        dic = {}
        for line in lines:
            dic[line.split(' ')[0]] = int(line.split(' ')[1])
        return dic

    # 读取语料库 199801_seg.txt
    # begining of the sentence is a single word?(S) or a cuple of words?(B)
    def count_init_prob(self, seg_lists):
        # 保存初始矩阵
        init = {
            'B': 0,
            'M': 0,
            'E': 0,
            'S': 0
        }
        # count for each word
        for seg_list in seg_lists:
            # single
            if len(seg_list[0]) == 1:
                init['S'] += 1
            # B M E
            else:
                init['B'] += 1
        # 归一化
        total = init['B'] + init['S']
        init['B'] = math.log(init['B'] / total)
        init['S'] = math.log(init['S'] / total)
        # 平滑处理
        init['M'] = self.inf
        init['E'] = self.inf
        with open('files/init_prob.json', 'w') as f:
            json.dump(init, f, indent=2)

    # 计算转移概率
    # BM BE MM ME ES EB SS SB
    def count_trans_prob(self, seg_lists):
        # save the trans prob
        trans = {
            'B': {},
            'M': {},
            'E': {},
            'S': {}
        }
        # TODO think about stop words
        for line in seg_lists:
            for i, word in enumerate(line):
                # think in the word, BM BE MM ME
                if len(word) == 2:
                    trans['B']['E'] = trans['B'].setdefault('E', 0) + 1
                elif len(word) >= 3:
                    trans['B']['M'] = trans['B'].setdefault('M', 0) + 1
                    trans['M']['M'] = trans['M'].setdefault(
                        'M', 0) + len(word) - 3
                    trans['M']['E'] = trans['M'].setdefault('E', 0) + 1
                # think between two words, SS SB ES EB
                if i:
                    if len(line[i - 1]) == 1 and len(word) == 1:
                        trans['S']['S'] = trans['S'].setdefault('S', 0) + 1
                    elif len(line[i - 1]) > 1 and len(word) == 1:
                        trans['E']['S'] = trans['E'].setdefault('S', 0) + 1
                    elif len(line[i - 1]) > 1 and len(word) > 1:
                        trans['E']['B'] = trans['E'].setdefault('B', 0) + 1
                    else:
                        trans['S']['B'] = trans['S'].setdefault('B', 0) + 1
        # 计算总次数
        total = {}
        for s in self.state:
            for s1 in self.state:
                total[s] = trans[s].setdefault(s1, 0) + total.setdefault(s, 0)
        # normalization
        for s in self.state:
            for s1 in self.state:
                if not trans[s][s1]:
                    trans[s][s1] = self.inf
                else:
                    # log
                    trans[s][s1] = math.log(trans[s][s1] / total[s])
        # save in the file
        with open('files/trans_prob.json', 'w') as f:
            json.dump(trans, f, indent=2)

    # 计算发射概率
    # input dic.txt (from 199801_seg.txt)
    # prob of each word in B or M or E or S
    # TODO 加权处理 发射概率乘以在总字数中的占比
    def count_emission_prob(self, dic):
        # save the emission prob matrix
        emission = {
            'B': {},
            'M': {},
            'E': {},
            'S': {}
        }
        # total time of each word
        total = {}
        total_words = 0
        # count for each word
        for word in dic.keys():
            # sign B M E S
            for i, w in enumerate(word):
                # 总频数 = Σ出现该字的词的频数
                total[w] = total.setdefault(w, 0) + dic.get(word)
                total_words += dic.get(word)

                # single
                if len(word) == 1:
                    emission['S'][w] = emission[
                                           'S'].setdefault(w, 0) + dic.get(word)
                # begin
                elif i == 0:
                    emission['B'][w] = emission[
                                           'B'].setdefault(w, 0) + dic.get(word)
                # end
                elif i == len(word) - 1:
                    emission['E'][w] = emission[
                                           'E'].setdefault(w, 0) + dic.get(word)
                # the middle word
                else:
                    emission['M'][w] = emission[
                                           'M'].setdefault(w, 0) + dic.get(word)
        # normalization
        for word in total.keys():
            for s in self.state:
                # 不存在则取0, 加1法平滑
                if word in emission[s]:
                    emission[s][word] = math.log(emission[s].get(word, 0) / total[word])
        # save emission prob matrix
        with open('files/emission_prob1.json', 'w') as f:
            json.dump(emission, f, indent=2)

CountProb()
