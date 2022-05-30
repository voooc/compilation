# -*- coding: utf-8 -*-
import pandas as pd
from 编译原理.complier.lexer.LeicalAnalysis import LeicalAnalysis
import random
from graphviz import Digraph


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        result = self.stack[-1]
        del self.stack[-1]
        return result

    def top(self):
        result = self.stack[-1]
        return result


def random_color():
    color_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    color = ""
    for i in range(6):
        color += color_list[random.randint(0, 14)]
    return "#" + color


class Recursive:
    def __init__(self, tokens, sentences, df, start):
        self.sentences = sentences
        self.tokens = tokens
        self.count = 0
        self.node_counts = 0
        self.start = start
        self.errors = ""
        # df = pd.read_csv('../data/grammar - 副本.csv', encoding='utf-8', header=None)
        self.grammar = {}
        self.terminator = []
        for i in range(len(df)):
            temp = df.iloc[i][1].split("|")
            res = []
            for j in range(len(temp)):
                res.append(temp[j].split(" "))
            self.grammar.update({df.iloc[i][0]: res})
        self.non_terminator = list(set(self.grammar.keys()))
        self.non_terminator.sort(key=list(self.grammar.keys()).index)
        for key, value in self.grammar.items():
            for i in value:
                for j in i:
                    if j not in self.terminator and j not in self.non_terminator:
                        self.terminator.append(j)
        self.first = {i: list() for i in self.non_terminator}
        self.follow = {i: list() for i in self.non_terminator}
        self.first_candidate = {i+'->' + '~'.join(j): list() for i in self.non_terminator for j in self.grammar[i]}
        self.g = Digraph(name="GrammarTree", format='pdf')

    def paint_edge(self, color, father, son):
        self.g.edge(father, son, color=color)

    def create_node(self, color, label):
        self.node_counts += 1
        self.g.node(name=str(self.node_counts), color=color, label=label, fontname="FangSong")

    def cal_fist(self, vn):
        for candidate in self.grammar[vn]:
            "产生式形如A-->aα,α∈Vt   以及 A--->$"
            if candidate[0] not in self.non_terminator:
                self.first[vn].append(candidate[0])
                self.first_candidate[vn+'->' + '~'.join(candidate)].append(candidate[0])
            else:
                "形如A-->X1X2X3...Xk,把First(X1)加入到First(A)中，如果X1--->$，将X2的First加入到A中"
                index = 0
                while index < len(candidate):
                    if candidate[index] in self.non_terminator:
                        "如果此时的元素，first集为空，先求first集合"
                        if self.first[candidate[index]] == list():
                            self.cal_fist(candidate[index])
                        self.first[vn] += self.first[candidate[index]]
                        temp = self.first[candidate[index]][:]
                        if '$' in self.first[candidate[index]]:
                            temp.remove('$')
                            self.first_candidate[vn + '->' + '~'.join(candidate)] += temp
                            index += 1
                            if index == len(candidate):
                                self.first_candidate[vn + '->' + '~'.join(candidate)].append('$')
                        else:
                            self.first_candidate[vn + '->' + '~'.join(candidate)] += temp
                            break
                    else:
                        break
            self.first_candidate[vn+'->'+'~'.join(candidate)] = list(set(self.first_candidate[vn+'->'+'~'.join(candidate)]))
        self.first[vn] = list(set(self.first[vn]))

    def get_fist(self):
        for _ in range(2):
            for key in self.grammar:
                self.cal_fist(key)

    def cal_follow(self, vn):
        for candidate in self.grammar[vn]:
            for index in range(len(candidate)):
                if candidate[index] in self.non_terminator:
                    "产生式B-->αAaβ，把a加入到Follow(A)中"
                    if index+1 < len(candidate) and candidate[index + 1] not in self.non_terminator:
                        self.follow[candidate[index]].append(candidate[index+1])
                    elif index+1 == len(candidate):
                        "β--->αA，Follow(B)加入到Follow(A)中"
                        self.follow[candidate[index]] += self.follow[vn]
                    elif candidate[index+1] in self.non_terminator:
                        "B---->αAβ，把First(β)中的非$元素加入到Follow(A)中"
                        if list('$') in self.grammar[candidate[index+1]]:
                            "B--->$,Follow(B)加入到Follow(A)中"
                            self.follow[candidate[index]] += self.follow[vn]
                        temp = self.first[candidate[index+1]][:]
                        if '$' in temp:
                            temp.remove('$')
                        self.follow[candidate[index]] += temp
                    self.follow[candidate[index]] = list(set(self.follow[candidate[index]]))

    def get_follow(self):
        self.follow[list(self.grammar.keys())[0]].append('#')
        for _ in range(2):
            for key in self.grammar:
                self.cal_follow(key)

    def is_left_recursion(self):
        errors = []
        for key in self.grammar:
            for candidate in self.grammar[key]:
                if candidate[0] == key:
                    errors.append((key, self.grammar[key]))
                    break
        if not errors:
            return True
        else:
            print("含有左递归")
            return False

    def is_candidate_first_intersect(self):
        temp = {i: list() for i in self.non_terminator}
        for i in self.first_candidate:
            for j in self.first_candidate[i]:
                temp[i.split('->')[0]].append(j)
        for i, j in temp.items():
            if len(j) != len(set(j)):
                print(j)
                print(i)
                print("候选式的首终结符集存在相交")
                return False
        return True

    def is_first_follow_intersect(self):
        for i in self.grammar:
            if self.grammar[i][0] == list('$'):
                if self.first[i].intersection(self.follow[i]):
                    print("首终结符集，包含$，first集和follow集有交集")
                    return False
        return True

    def is_ll1(self):
        if not self.is_left_recursion() and not self.is_candidate_first_intersect() and not self.is_first_follow_intersect():
            return False
        return True

    def analyze(self, father, node):
        for i in range(len(self.grammar[node])):
            color = random_color()
            if self.count == len(self.tokens):
                break
            if self.tokens[self.count] in self.first_candidate[node+'->'+'~'.join(self.grammar[node][i])]:
                for j in self.grammar[node][i]:
                    if j in self.non_terminator:
                        color = random_color()
                        self.create_node(color=color, label=j)
                        self.paint_edge(color=color, father=father, son=str(self.node_counts))
                        self.analyze(str(self.node_counts), j)
                    else:
                        if j == self.tokens[self.count]:
                            self.create_node(color=color, label=self.sentences[self.count])
                            self.paint_edge(color=color, father=father, son=str(self.node_counts))
                            self.count += 1
                            # if self.count == len(self.tokens):
                            #     self.create_node(color=color, label='$')
                            #     self.paint_edge(color=color, father=father, son=str(self.node_counts))
                            #     self.g.view(filename='grammar_tree')
                            #     exit()
                        else:
                            print("error1")
                            return
                break
            else:
                if i == len(self.grammar[node]) - 1:
                    if self.tokens[self.count] in self.follow[node] and \
                            '$' in self.first[node]:
                        self.create_node(color=color, label='$')
                        self.paint_edge(color=color, father=father, son=str(self.node_counts))
                    else:
                        if self.tokens[self.count] == '700':
                            self.errors = '变量声明未指定类型'
                            break
                        elif self.sentences[self.count] == 'return':
                            print("void 没有返回值")
                            self.errors = 'void 没有返回值'
                            break
                        elif self.sentences[self.count] == '(':
                            if node == 'c':
                                self.errors = "main函数缺失main"
                        elif self.sentences[self.count] == '{':
                            self.errors = "缺失）"
                        else:
                            print(self.sentences[self.count-1])
                            print(self.sentences[self.count])
                            print("error2")
                            break

    def parser(self):
        self.get_fist()
        self.get_follow()
        if not self.is_ll1():
            return False
        self.create_node('red', self.start)
        self.analyze(str(self.node_counts), self.start)
        if self.errors == '':
            self.g.view(filename='grammar_tree')
        else:
            pass
        return self.errors


def main():
    f = open(r'../../新版编译器测试用例/test1.txt', 'r', encoding='utf-8')
    with f:
        data = f.read()
    lexical = LeicalAnalysis(data)
    res, error = lexical.run()
    token = []
    sentences = []
    for i in res:
        token.append(i.split('\t')[1])
        sentences.append(i.split('\t')[2])
    if len(token) <= 0:
        print("请输入代码")
    elif len(error) != 0:
        print("语法有错误")
    else:
        df = pd.read_csv('../data/grammar - 副本.csv', encoding='utf-8', header=None)
        x = Recursive(token, sentences, df, '程序')
        x.parser()


if __name__ == '__main__':
    main()
