# -*- coding: utf-8 -*-
from hmm import HMM
from trie import Trie
import math

class Unigram:

    def __init__(self):
        # 字典树
        self.root = Trie()
        # 词概率
        self.word_freq = {}
        self.hmm = HMM()
        self.read_dic()

    # 读取词典并保存到字典树中
    def read_dic(self, dic='files/dic.txt'):
        with open(dic, 'r') as f:
            d = f.read()
            text = d.split('\n')
        total_times = 0
        for line in text:
            if (line != ""):
                words = line.split(" ")
                self.root.add(words[0])
                self.word_freq[words[0]] = int(words[1])
                total_times += int(words[1])
        for key in self.word_freq.keys():
            self.word_freq[key] = math.log(
                self.word_freq.get(key) / total_times)
        self.min_freq = self.word_freq.get(
            min(self.word_freq, key=self.word_freq.get))

    def cut(self, sentence, useHMM=False):
        # 最大词频切分
        ans = self.dp_search(sentence)
        # 将分词结果中的多个连续单个字传入HMM
        if (useHMM):
            segs = []
            temp = []
            for seg in ans:
                if len(seg) == 1:
                    temp.append(seg)
                else:
                    if len(temp) >= 5:
                        for word in self.hmm.Viterbi(''.join(w for w in temp)):
                            segs.append(word)
                    else:
                        for word in temp:
                            segs.append(word)
                    segs.append(seg)
                    temp = []

            if len(temp):
                for word in self.hmm.Viterbi(''.join(w for w in temp)):
                    segs.append(word)
            ans = segs

        return ans

    # DAG动态规划
    def dp_search(self, sentence):
        DAG = {}
        # 构建全有向切分图
        for i in range(0, len(sentence)):
            DAG[i] = self.root.scan(sentence[i:], i)
        # 保存路径
        route = {}
        # 边界情况
        route[len(sentence)] = (0.0, '')
        # 从最后一个字遍历到第一个字
        for i in range(len(sentence) - 1, -1, -1):
            # 求解的所有可能值
            temp = [(self.word_freq.get(sentence[i:x + 1],
                                        self.min_freq) + route[x + 1][0], x) for x in DAG[i]]
            # 选择最大值
            route[i] = max(temp)

        index = 0
        segs = []
        # 回溯切分结果
        while index < len(sentence):
            segs.append(sentence[index:route[index][1] + 1])
            index = route[index][1] + 1
        return segs
