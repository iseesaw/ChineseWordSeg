# coding=utf-8
class Trie:
    root = {}
    # 终结点
    END = '/'

    # 将词加入字典树
    def add(self, word):
        # 从根节点遍历单词,char by char,如果不存在则新增,最后加上一个单词结束标志
        node = self.root
        for c in word:
            node = node.setdefault(c, {})
        node[self.END] = None

    # 一个词是否在字典树中
    def contain(self, word):
        node = self.root
        for c in word:
            if c not in node:
                return False
            node = node[c]
        # 　判断是否为终结点
        return self.END in node

    # 扫描一个句子中, 所有以该字开始的单词
    def scan(self, sentence, index):
        cnt = index - 1
        result = [index]
        node = self.root
        for i, c in enumerate(sentence):
            if c not in node:
                return result
            node = node[c]
            cnt += 1
            if self.END in node and i:
                result.append(cnt)

        return result
