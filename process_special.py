# -*- coding: utf-8 -*-
import re

'''
对二元分词结果进行特殊处理
'''

class SpecialProcess:

    # 合并汉语数字+年月日、英语单词、连续的阿拉伯数字及小数点等
    # 使用FA处理数字、字母
    def special_process(self, bigram_segs):
        # 保存分词结果
        segs = []
        temp = []
        # 遍历bigram的分词结果
        for seg in bigram_segs:
            # 保存单个的词
            if len(seg) == 1:
                temp.append(seg)
            # 遇到多个字的词时处理之前的单个词序列
            else:
                # 处理连续单个词的集合
                if len(temp) >= 2:
                    specs = self.judge_nums_letters(temp)
                    for word in specs:
                        segs.append(word)
                else:
                    # 否则直接加入最终分词结果中
                    for word in temp:
                        segs.append(word)
                segs.append(seg)
                temp = []

        # 如果连续的单个词在句子最后，则单独判断
        if len(temp):
            for word in self.judge_nums_letters(temp):
                segs.append(word)
        return segs

    # 判断是否能组成一个词
    # 1.中文数字 若有结束符则加上结束符
    #   一万五千六百  百分之十五 二千二百零一点八
    # 2.英文字母
    #   Ｈｏｔｅｒ
    # 3.阿拉伯数字 + 结束符
    #   １２８９ ８５·５％ １０．９１亿/万/千 １９１０年/月/日/时/分/秒
    def judge_nums_letters(self, single_words):
        # 中文数字
        chinese_nums = {'分', '之', '点', '零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '亿', '○'}
        # 数字结束标志
        signal_ends = {'年', '月', '日', '时', '分', '秒', '％', '%', '‰'}
        # 全角数字 u'\uff10' - u'\uff19'
        full_nums = r'[\uff10-\uff19\.．·0-9]'
        p_nums = re.compile(full_nums)
        # 全角字母 u'\uff41' - u'\uff5a'
        # u'\uff21' - u'\uff3a'
        full_letters = r'[\uff41-\uff5a\uff21-\uff3aa-zA-Z]'
        p_letters = re.compile(full_letters)

        # 保存修改后的分词
        segs = []
        # 保存特殊词
        temp = []
        for w in single_words:
            # 保存特殊词
            if w in chinese_nums or p_letters.match(w) or p_nums.match(w):
                temp.append(w)
            # 如果是特殊词的结尾, 则把该词和之前的特殊词合并
            elif w in signal_ends:
                temp.append(w)
                if temp:
                    segs.append(''.join(temp))
                    temp = []
            else:
                # 不属于特殊词, 则把之前保存的特殊词合并
                if temp:
                    segs.append(''.join(temp))
                    temp = []

                segs.append(w)
        # 检查末尾是否有剩余
        if temp:
            segs.append(''.join(temp))

        return segs
