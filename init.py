# -*- coding: utf-8 -*-
'''
调用Unigram和HMM进行分词
'''
from config import *
from hmm import HMM
from bigram import Bigram
import time
import re
import codecs

if __name__ == "__main__":

    print('将对配置文件config.py中TESTFILE='+TESTFILE+'进行分词...')
    start = time.time()

    with codecs.open(TESTFILE, 'r', 'gbk') as f:
        text = f.read()
    lines = text.split('\r\n')

    bigram = Bigram()
    lines_segs = []
    # 逐行进行分词
    for i, line in enumerate(lines):
        line_segs = []
        if line != '':
            ###### 将每行从传入分词模型 #####
            line_segs = bigram.cut(line)
            ###############################
        else:
            line_segs = line

        lines_segs.append(line_segs)
        # 没千行打印耗时
        if i % 1000 == 0:
            print(str(i) + '/' + str(len(lines)), time.time() - start)

    print('分词完成...')
    end = time.time()
    print('takes ' + str(end - start)[:6] + 's')
    print('写入文件, 保存至seg_bigram_hmm.txt...')
    # 写入文件
    with open('seg_bigram_hmm.txt', 'w', encoding='GBK') as f:
        for n, line in enumerate(lines_segs):
            text = ''
            for w in line:
                # 斜杠空格分割
                if w != chr(13) and w != '':
                    text += w + '/ '
                else:
                    text += w
            f.write(text)
            if n != len(lines_segs) - 1:
                f.write('\n')
    print('写入完成...')
    end = time.time()
    print('takes ' + str(end - start)[:6] + 's')
