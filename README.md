## 基于Bigram+HMM的层次中文分词系统
### files
该文件夹包含以下输入文件  
199801_seg.txt  人民日报语料库  
199801_sent.txt  人民日报  
dic.txt  分词字典(通过199801_seg.txt计算)  
name.txt  姓名数据集  
first_name.txt  姓词频统计(通过name.txt计算)  
second_name.txt  名字词频统计(通过name.txt计算)  
bigram_dic.json  二元语言模型的概率文件(通过199801_seg.txt计算)  
init_prob.json  HMM初始概率矩阵(通过199801_seg.txt计算)  
emission_prob.json  HMM发射概率矩阵(通过199801_seg.txt计算)  
trans_prob.json  HMM转移概率矩阵(通过199801_seg.txt计算)  
emission_prob_v2.json  HMM_v2发射概率矩阵(通过199801_seg.txt计算)  
**换行问题** windows下均以\r\n换行, 因此读取文件后均以\r\n分割  


### 基于统计语言模型的分词系统实现代码(最终代码文件)
#### init.py
主程序文件, 将对config.py中TESTFILE进行分词  
读取测试文件, 按行分割并将每行传入bigram进行分词  
最后保存分词结果将保存在该目录下,命名为seg_bigram_hmm.txt  
(关于换行问题, 在第19行对输入文件用'\r\n'分割)

#### config.py
配置文件  
包含词典、199801_seg.txt语料库位置, 以及**测试文件位置**  
可通过修改**TESTFILE**指定测试文件

#### bigram.py
分词系统的主要代码  
实现二元分词模型  
对二元分词结果首先调用特殊字处理  
然后将连续多个单字传入HMM, 对结果调用姓名处理程序  
最后再将剩余连续多个单字进行概率(发射S概率小于某一阈值)判断再传入HMM    
可通过调用Bigram().cut(sentence)对句子sentence进行分词   
集内测试99.6%

#### hmm.py
实现HMM的代码  
状态集为常用的[S, B, M, E], 标识一个字在一个词中的位置  
调用方法为HMM().Viterbi(sentence), 返回该句子的分词结果    
主要实现维特比算法

#### count_prob.py
输入199801语料库文件, 计算初始概率矩阵、转移概率矩阵和发射概率矩阵

####  process_name.py
对姓名进行分词(分词标准是将姓和名分开的)相关代码(统计作为姓名的常用字及词频)  
对bigram的分词结果进行处理  
将连续多个字传入HMM, 对HMM的分词结果进行名字评价判断  
评价公式为: l*∑ci  
l为当前分词长度  
∑ci表示当前分词中每个字作为名的词性, 以及前一个分词作为姓的词性  
根据研究, 将name.txt中作为名的字频次大于500的词性设为3  
将name.txt中作为姓的字频次大于100的词性设为3  
其余字词性设为1, 计算结果不小于14的分词判别为名字, 否则拆成单字

#### process_special.py
英文字母、数量词等特殊处理代码  
对bigram的分词结果进行特殊处理  
对连续的多个单个英文字母、数字等进行合并  
主要是使用有限自动机思想 

#### trie.py
数据结构Trie树的实现  
通过扫描Trie树构建全有向切分图

### 其他尝试性代码(不包含在最终统计语言模型分词系统中)
#### unigram.py
一元语言模型(最大词频分词)实现代码  
实验中尝试性结合HMM进行分词(参考jieba实现), 具体是:   
先使用unigram进行分词  
然后将分词结果中多个连续的单个字传入HMM进行分词  
调用方法Unigram().cut(sentence, useHMM=false)
可选择是否调用HMM, 返回该句子分词结果    
实际效果不好, HMM会分出未登录词, 但大概率降低unigram性能  
集内测试90%左右

#### hmm_v2.py
关于基于字位信息的中文分词方法的实现代码(不妨称为HMM_v2)  
在基本HMM实现中, 加入当前字前面字的信息, 实现联系上下文的效果  
调用方法为HMM_v2().Viterbi(sentence), 返回该句子的分词结果    
实际分词效果较差, 大概率受限于训练语料库的大小  
集内测试70%左右

#### count_prob_v2.py
计算HMM_v2的发射概率矩阵的代码文件  
计算形式为
emission_prob[s][wi][wi-1]  
表示字wi在前面一个字为wi-1的条件下表现为s状态的概率





