# -*- coding: utf-8 -*-
'''
二元语法模型
词典存储结构
w 表示当前词、wi表示该词前面的词及次数
{
    w:{
        w1: c1
        w2: c2
        w3: c3
    }
}
'''
from config import *
from trie import Trie
from process_special import SpecialProcess
from hmm import HMM
import re
import math
import json
import codecs

class Bigram:

    def __init__(self):
        # TODO 测试集上检查平滑处理的抉择问题
        self.minfreq = -3.14e+100
        # 构建字典树、用于扫描全切分有向图
        self.trie = Trie()
        self.construct_trie()
        # 构建 二元词典
        # self.construct_bigram_dic()
        # 读取二元词典
        with open('files/bigram_dic.json', 'r') as f:
            self.bigram_dic = json.load(f)

        # 进行特殊处理
        self.SP = SpecialProcess()

        # 创建HMM分词模型
        self.hmm = HMM()

        # 获取常用姓名中名字
        self.get_second_names()
        self.get_first_name()

    # 构建字典树
    def construct_trie(self, dic_file=DICFILE):
        with codecs.open(dic_file, 'r', 'gbk') as f:
            d = f.read()
            text = d.split('\r\n')
        # unigram
        # self.unigram = {}
        # unigram_time = 0
        self.words_num = len(text)
        for line in text:
            if (line != ""):
                words = line.split(" ")
                # self.unigram[words[0]] = int(words[1])
                # unigram_time += int(words[1])
                self.trie.add(words[0])
        # 词频词典
        # for key in self.unigram.keys():
        #    self.unigram[key] = math.log(self.unigram.get(key) / unigram_time)

    # 构建二元词典
    def construct_bigram_dic(self, seg_file=BIDICFILE):
        with codecs.open(seg_file, 'r', 'gbk') as f:
            text = f.read()
        lines = text.split('\r\n')
        seg_lists = []
        # 按行提取分词结果
        for line in lines:
            # 遇到空白行直接进行下一行
            pattern = re.compile(r'^199801')
            # 未匹配下一行
            if not re.match(pattern, line):
                continue
            # 将每行正则匹配  Word/sign 包括 [Word/sign
            regex = r'\s[^\s^/]+/\w+'
            segs = re.findall(regex, line)
            # 处理匹配得到的字符
            seg_list = []
            for seg in segs:
                # 去除可能的[、同时去除匹配首位的空格
                s = seg.replace('[', '')[1:]
                word = s.split('/')[0]
                # 该行所有分词
                seg_list.append(word)
            # 首位插入BOS
            seg_list.insert(0, "^")
            # 尾部插入EOS
            seg_list.append("$")
            # 保存每行分词结果
            seg_lists.append(seg_list)
        # 构造bigram词典
        self.bigram_dic = {}
        # 遍历每行
        for seg_list in seg_lists:
            # 从第二个分词（第一个是BOS）遍历每行的分词语料
            for i in range(1, len(seg_list)):
                # 第一次遇到
                if seg_list[i] not in self.bigram_dic:
                    self.bigram_dic[seg_list[i]] = {}
                    # 保存该词前面的词
                    self.bigram_dic[seg_list[i]][seg_list[i - 1]] = 1
                else:
                    self.bigram_dic[seg_list[i]][seg_list[i - 1]] = self.bigram_dic[seg_list[i]].get(seg_list[i - 1],
                                                                                                     0) + 1
        # 频数转换为概率, 取对数
        for key1 in self.bigram_dic.keys():
            sigma = 1e-7
            sum_freq = 0
            for key2 in self.bigram_dic.get(key1).keys():
                sum_freq += self.bigram_dic[key1].get(key2)
            # 求c(wi-1wi)/ c(wi)概率
            for key2 in self.bigram_dic.get(key1).keys():
                self.bigram_dic[key1][key2] = math.log(
                    (self.bigram_dic[key1].get(key2) + sigma) / (sum_freq + sigma * self.words_num))
                # add(sigma)
                temp = math.log(sigma / (sum_freq + self.words_num))
                if self.minfreq > temp:
                    self.minfreq = temp
        # with open('bigram_dic.json', 'w') as f:
        #     json.dump(self.bigram_dic, f)
        # print(self.minfreq)

    # 构建全切分有向图
    def construct_DAG(self, sentence):
        # {key:list}
        self.DAG = {}
        # ^ - $
        for i in range(1, len(sentence) - 1):
            # 保存以wi开始的词
            self.DAG[i] = self.trie.scan(sentence[i:-1], i)
        # 加EOS和BOS
        self.DAG[len(sentence) - 1] = [len(sentence) - 1]
        self.DAG[0] = [0]

    def dp_search(self, sentence):
        # prob max
        viterbi = {}
        for i in range(len(sentence)):
            viterbi[i] = {}
        # { i :{ end1: (prob, next), end2 : (prob, next) }}
        viterbi[len(sentence) - 1][len(sentence) - 1] = (0., len(sentence))
        # 反向DP
        for i in range(len(sentence) - 2, -1, -1):
            # 对每个wi起始的词求最大概率
            for x in self.DAG[i]:
                # P(wx+1...wy | wi..wx)*viterbi[x+1][index][0]
                prob_index = max(
                    (self.bigram_dic.get(sentence[x + 1:y + 1], {}).get(sentence[i:x + 1], self.minfreq) +
                     viterbi.get(x + 1)[y][0], y) for y in self.DAG[x + 1])
                viterbi[i][x] = prob_index

        # BOS
        end = max((self.bigram_dic.get(sentence[1:y + 1], {}).get(sentence[0], self.minfreq) +
                   viterbi.get(1)[y][0], y) for y in self.DAG[1])[1]
        # 回溯*
        start = 1
        segs = []
        while start < len(sentence) - 1:
            segs.append(sentence[start:end + 1])
            temp = start
            start = end + 1
            # print(viterbi[temp][end][0])
            end = viterbi[temp][end][1]
        return segs

    # 调用bigram分词并做后续处理
    def cut(self, sentence):
        sentence = '^' + sentence + '$'
        # 构建句子 全切分有向图
        self.construct_DAG(sentence)
        # 得到bigram分词结果
        bigram_segs = self.dp_search(sentence)

        # 汉语数字、阿拉伯数字、英语单词、年月日等标志词的处理
        deal_segs = self.SP.special_process(bigram_segs)

        # hmm识别姓名
        hmm_segs = self.hmm_for_single_words(deal_segs)

        return hmm_segs

    # 将bigram分词结果中多个连续的单个词传入hmm进行分词
    def hmm_for_single_words(self, bigram_segs):
        # 保存hmm的分词结果
        segs = []
        temp = []
        # 遍历bigram的分词结果
        for seg in bigram_segs:
            # 保存单个的词
            if len(seg) == 1:
                temp.append(seg)
            # 遇到多个字的词时处理之前的单个词序列
            else:
                # 处理连续三个单个词的集合
                if len(temp) >= 3:
                    # 作为整体传入hmm并得到分词结果
                    hmm_segs = self.hmm.Viterbi(''.join(w for w in temp))
                    # 进行姓名识别
                    oov_segs = self.OOV_name(hmm_segs)
                    # # # # 进行OOV识别 TODO
                    if len(oov_segs) == len(temp):
                        oov_segs = self.OOV(temp)

                    for word in oov_segs:
                        segs.append(word)
                else:
                    # 否则直接加入最终分词结果中
                    for word in temp:
                        segs.append(word)
                segs.append(seg)
                temp = []

        # 如果连续的单个词在句子最后，则单独判断
        if len(temp):
            # 作为整体传入hmm并得到分词结果
            hmm_segs = self.hmm.Viterbi(''.join(w for w in temp))
            # 进行OOV姓名识别
            oov_segs = self.OOV_name(hmm_segs)
            # # # # 进行OOV识别 TODO
            if len(oov_segs) == len(temp):
                oov_segs = self.OOV(temp)

            for word in oov_segs:
                segs.append(word)

        # 返回HMM的最后分词结果
        return segs

    # 采用一些手段进行OOV的识别
    # 单个分词中的未登录词处理
    # 调用获得HMM分词结果
    # 对合并的词进行姓名打分
    # 姓名的判断 rl*l*sum(ci) > 2*(3+3+1)
    # TODO 其他未登录词的打分机制和判断机制
    def OOV_name(self, hmm_segs):
        oov_segs = []
        # 遍历HMM分的词
        for i, seg in enumerate(hmm_segs):
            # 单个词直接加入
            if len(seg) == 1:
                oov_segs.append(seg)
            # 否则识别是否为姓名
            # TODO 姓名的判断阈值
            else:
                # 打分
                score = 0
                # 判断是否为名
                for w in seg:
                    if w in self.second_names and self.second_names.get(w, 0) > 500:
                        score += 3
                    else:
                        score += 1
                # 判断是否为姓
                if i > 0 and hmm_segs[i - 1] in self.first_names and self.first_names.get(hmm_segs[i - 1], 0) > 100:
                    score += 3
                # 判断分数, 大于14则加入分词结果
                # TODO 阈值判断
                if score * len(seg) >= 14:
                    oov_segs.append(seg)
                # 不是未登录词
                else:
                    # 将单个词加入分词结果
                    for w in seg:
                        oov_segs.append(w)
        return oov_segs

    # 获取常用名字
    def get_second_names(self):
        with codecs.open('files/second_name.txt', 'r', 'gbk') as f:
            file = f.read()
        # 不要最后一个空行
        lines = file.split('\r\n')[:-1]
        self.second_names = {}
        for line in lines:
            # 获得名字和频次
            words = line.split(' ')
            self.second_names[words[0]] = int(words[1])

    def get_first_name(self):
        with codecs.open('files/first_name.txt', 'r', 'gbk') as f:
            file = f.read()
        # 不要最后一个空行
        lines = file.split('\r\n')[:-1]
        self.first_names = {}
        for line in lines:
            # 获得名字和频次
            words = line.split(' ')
            self.first_names[words[0]] = int(words[1])

    # 判断多个单个词是否传入HMM进行分词
    def OOV(self, temp):
        single_nums = 0
        for w in temp:
            if self.hmm.emission_prob['S'].get(w, 0) < -3.5:
                single_nums += 1
        if single_nums >= 2:
            hmm_segs = self.hmm.Viterbi(''.join(temp))
            return hmm_segs
        else:
            return temp

