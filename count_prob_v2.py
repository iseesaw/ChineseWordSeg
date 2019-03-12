# -*- coding: utf-8 -*-
'''
基于词位信息的HMM中文分词算法
'''
from config import *
import json
import codecs
import re
import math

class Count:
    def __init__(self, seg_file=BIDICFILE, dic_file=DICFILE):
        # 平滑
        self.inf = -3.14e+100
        # B M E S
        self.state = ['B', 'M', 'E', 'S']
        # 获取训练集
        self.seg_lists = self.analysis_seg_file(seg_file)
        self.dic = self.analysis_dic_file(dic_file)
        # 训练参数
        self.count_emit(self.dic)

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

    # Count(oj-1oj, ci) / Count(ci)
    # 保存oj处于每个标志且上一个字为oj-1的概率
    def count_emit(self, dic):
        # save the emission prob matrix
        emission = {
            'B': {},
            'M': {},
            'E': {},
            'S': {}
        }
        # total time of each word
        total = {}
        # count for each word
        for word in dic.keys():
            # sign B M E S
            for i, w in enumerate(word):
                # 总频数 = Σ出现该字的词的频数
                total[w] = total.get(w, 0) + dic.get(word)

                # single
                if len(word) == 1:
                    if w not in emission['S']:
                        emission['S'][w] = {}
                    # 前面没有字, 则将本身的概率保存为None
                    emission['S'][w][-1] = emission[
                                               'S'][w].setdefault(-1, 0) + dic.get(word)
                # begin
                elif i == 0:
                    if w not in emission['B']:
                        emission['B'][w] = {}
                    emission['B'][w][-1] = emission[
                                               'B'][w].setdefault(-1, 0) + dic.get(word)
                # end
                elif i == len(word) - 1:
                    if w not in emission['E']:
                        emission['E'][w] = {}
                    emission['E'][w][word[i - 1]] = emission[
                                                        'E'][w].setdefault(word[i - 1], 0) + dic.get(word)
                # the middle word
                else:
                    if w not in emission['M']:
                        emission['M'][w] = {}
                    emission['M'][w][word[i - 1]] = emission[
                                                        'M'][w].setdefault(word[i - 1], 0) + dic.get(word)
        # normalization
        for word in total.keys():
            for s in self.state:
                # word可能没有s状态,则无法使用keys, 不判断会出错误
                if emission[s].get(word):
                    for key in emission[s][word].keys():
                        # 不存在则取0, 加1法平滑
                        emission[s][word][key] = math.log(emission[s][word].get(key) / total[word])
        # save emission prob matrix
        with open('files/emission_prob_v2.json', 'w') as f:
            json.dump(emission, f, indent=2)

Count()
