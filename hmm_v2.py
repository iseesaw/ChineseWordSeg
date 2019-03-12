# -*- coding: utf-8 -*-
'''
achieve Viterbi Algorithm
solve OOV
'''
from collections import defaultdict
import json
import math

class HMM_v2:

    def __init__(self):
        # read prob from files
        self.get_prob()

    def get_prob(self):
        with open('files/init_prob.json', 'r') as f:
            self.init_prob = json.load(f)
        with open('files/trans_prob.json', 'r') as f:
            self.trans_prob = json.load(f)
        with open('files/emission_prob_v2.json', 'r') as f:
            self.emission_prob = json.load(f)
        # TODO: find the best solution for not exists word in emission_prob.json - 0.25?
        self.min_freq = -3.14e+100

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
            # 第一个字, 则是发射矩阵中这个字的该状态下, 前一个没有字-取-1的概率, 如果没有则平滑
            viterbi[0][s] = (
                self.init_prob[s] + self.emission_prob[s].get(sentence[0], {}).setdefault(-1, self.min_freq),
                -1)
        # Viterbi过程
        # travers from the second word, i start from the first word
        for i in range(length - 1):
            # 遍历该位置的每个状态
            for s in states:
                # 遍历前置节点的所有状态转移
                # self.emission_prob[s].setdefault(w, 1) - if w not in the
                # 找该状态下 该字且在前一个字的状态的 概率
                # 如果前一个字没有, 则取该字处于该状态下的概率,
                # 其余情况平滑
                viterbi[i + 1][s] = max([(viterbi[i][s1][0] + self.trans_prob[s1].get(s) + self.emission_prob[
                    s].get(sentence[i + 1], {}).setdefault(sentence[i],
                                                           self.emission_prob[s].get(sentence[i + 1], {}).setdefault(-1,
                                                                                                                     self.min_freq)),
                                          s1) for s1 in states])

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

        return segs