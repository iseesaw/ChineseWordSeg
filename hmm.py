# -*- coding: utf-8 -*-
'''
achieve Viterbi Algorithm
solve OOV
'''
from collections import defaultdict
import json
import math

class HMM:

    def __init__(self):
        # read prob from files
        self.get_prob()

    def get_prob(self):
        with open('files/init_prob.json', 'r') as f:
            self.init_prob = json.load(f)
        with open('files/trans_prob.json', 'r') as f:
            self.trans_prob = json.load(f)
        with open('files/emission_prob.json', 'r') as f:
            self.emission_prob = json.load(f)
        # TODO: find the best solution for not exists word in emission_prob.json - 0.25?
        self.min_freq = math.log(0.25)

    def Viterbi(self, sentence):
        # 所有状态
        states = ['B', 'M', 'E', 'S']
        length = len(sentence)
        # (Viterbi variable, state before si)
        viterbi = {}
        for i in range(len(sentence)):
            viterbi[i] = {}
        # init(i) + b0(i)

        for s in states:
            viterbi[0][s] = (self.init_prob[s] + self.emission_prob[s].setdefault(sentence[0], self.min_freq), -1)
        # Viterbi过程
        # travers from the second word, i start from the first word
        for i in range(length - 1):
            # 遍历该位置的每个状态
            for s in states:
                # 遍历前置节点的所有状态转移
                # self.emission_prob[s].setdefault(w, 1) - if w not in the
                viterbi[i + 1][s] = max([(viterbi[i][s1][0] + self.trans_prob[s1].get(s) + self.emission_prob[
                    s].setdefault(sentence[i + 1], self.min_freq), s1) for s1 in states])

        sign = [None] * length
        #####################
        # 关于最后一个字的抉择
        # 1、在 E S两个状态中选出维特比变量最大的一个
        # 2、先选出维特比变量最大的一个, 然后判断是否是E or S, 如果不是则修改
        #####################
        # sign[-1] = max(viterbi[length - 1], key=viterbi[length - 1].get)

        # the last one should be E or S, choose the max prob one 
        sign[-1] = max((viterbi[length - 1][s], s) for s in 'ES')[1]

        # 回溯
        for n in range(length - 2, -1, -1):
            sign[n] = viterbi[n + 1][sign[n + 1]][1]
            # print(viterbi[n + 1][sign[n + 1]][0])

        # # the last one word should be S Or E
        # if sign[-1] != 'S' and sign[-1] != 'E':
        #     if sign[-2] != 'S':
        #         sign[-1] = 'E'
        #     else:
        #         sign[-1] = 'S'
        #######################

        # 标注by B E S
        start = 0
        segs = []
        for index, s in enumerate(sign):
            if s == 'S':
                segs.append(sentence[index])
            elif s == 'B':
                start = index
            elif s == 'E':
                end = index + 1
                segs.append(sentence[start:end])
        # # 打印每个词的概率
        # # bt(i) aij bt+1(j)
        # bi_dic = {}
        # for i, seg in enumerate(segs[1:]):
        #     prob = self.prob_word(segs[i]) + self.prob_word(seg)
        #     if len(segs[i]) == 1 and len(seg) == 1:
        #         prob += self.trans_prob['S']['S']
        #     elif len(segs[i]) > 1 and len(seg) == 1:
        #         prob += self.trans_prob['E']['S']
        #     elif len(segs[i]) == 1 and len(seg) > 1:
        #         prob += self.trans_prob['S']['B']
        #     else:
        #         prob += self.trans_prob['E']['B']
        #     if seg not in bi_dic:
        #         bi_dic[seg] = {}
        #     bi_dic[seg][segs[i]] = prob
        return segs

    # 获得该字的概率
    def prob_word(self, word):
        if len(word) == 1:
            return self.emission_prob['S'].setdefault(word, self.min_freq)
        elif len(word) == 2:
            return self.emission_prob['B'][word[0]] + self.emission_prob['E'][word[1]] + self.trans_prob['B']['E']
        else:
            prob = self.emission_prob['B'][word[0]] + self.emission_prob['E'][word[-1]] + self.trans_prob['B']['M'] + \
                   self.trans_prob['M']['E']
            prob = prob + self.emission_prob['M'][word[1]]
            for i, w in enumerate(word[2:-1]):
                prob = prob + self.emission_prob['M'][word[2 + i]] + self.trans_prob['M']['M']

