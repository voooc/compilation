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
    def __init__(self, tokens, sentences):
        self.sentences = sentences
        self.tokens = tokens
        self.count = 0
        self.node_counts = 0
        df = pd.read_csv('../data/grammar - 副本.csv', encoding='utf-8', header=None)
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
        self.first_candidate = {i + '->' + '~'.join(j): list() for i in self.non_terminator for j in self.grammar[i]}
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
                self.first_candidate[vn + '->' + '~'.join(candidate)].append(candidate[0])
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
            self.first_candidate[vn + '->' + '~'.join(candidate)] = \
                list(set(self.first_candidate[vn + '->' + '~'.join(candidate)]))
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
                    if index + 1 < len(candidate) and candidate[index + 1] not in self.non_terminator:
                        self.follow[candidate[index]].append(candidate[index + 1])
                    elif index + 1 == len(candidate):
                        "β--->αA，Follow(B)加入到Follow(A)中"
                        self.follow[candidate[index]] += self.follow[vn]
                    elif candidate[index + 1] in self.non_terminator:
                        "B---->αAβ，把First(β)中的非$元素加入到Follow(A)中"
                        if list('$') in self.grammar[candidate[index + 1]]:
                            "B--->$,Follow(B)加入到Follow(A)中"
                            self.follow[candidate[index]] += self.follow[vn]
                        temp = self.first[candidate[index + 1]][:]
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
        for i in temp:
            if len(temp[i]) != len(set(temp[i])):
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
        if not self.is_left_recursion() and not self.is_candidate_first_intersect() \
                and not self.is_first_follow_intersect():
            return True
        return False

    # 复合语句
    def compound_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '301':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='语句表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '302':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("表达式缺失}")
                return False

        elif self.tokens[self.count] in self.follow['复合语句'] and '$' in self.first['复合语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("有错")
            return False

    # 语句表
    def statement_table(self, father):
        color = random_color()
        if self.tokens[self.count] == '119':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='常量类型')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant_type(str(self.node_counts)):
                return False

            self.create_node(color=color, label='常量声明表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant_declaration_table(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '103':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '104':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '102':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '101':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '101':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1

            if self.tokens[self.count] == '700':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失函数名")
                return False

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='函数定义形参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definite_formal_parameters_list(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '700':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='Q')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.first_candidate['语句表->' + '~'.join(self.grammar['语句表'][6])]:
            self.create_node(color=color, label='e')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ea(str(self.node_counts)):
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '301':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='语句表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '302':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失}")
                return False

            self.create_node(color=color, label='K')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.k(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['语句表'] and '$' in self.first['语句表']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # e
    def ea(self, father):
        color = random_color()
        if self.tokens[self.count] == '125':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失(")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            self.create_node(color=color, label='语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='L')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.l(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '130':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失(")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失(")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            self.create_node(color=color, label='循环语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '132':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失(")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失)")
                return False

            self.create_node(color=color, label='循环语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '131':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='循环用复合语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_with_statement(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '132':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失while")
                return False

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失(")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失)")
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

        elif self.tokens[self.count] == '121':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='0')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.o(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['e'] and '$' in self.first['e']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # O
    def o(self, father):
        color = random_color()
        if self.tokens[self.count] == '303':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] in self.first_candidate['O->' + '~'.join(self.grammar['O'][1])]:
            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1

        elif self.tokens[self.count] in self.follow['O'] and '$' in self.first['O']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # break语句
    def break_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '123':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1

            else:
                print("缺失;")
                return False

        elif self.tokens[self.count] in self.follow['break语句'] and '$' in self.first['break语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # continue语句
    def continue_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '122':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1

            else:
                print("缺失;")
                return False

        elif self.tokens[self.count] in self.follow['continue语句'] and '$' in self.first['continue语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 循环用复合语句
    def loop_with_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '301':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='循环语句表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement_table(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '302':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失}")
                return False

        elif self.tokens[self.count] in self.follow['循环用复合语句'] and '$' in self.first['循环用复合语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 循环语句
    def loop_statement(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['循环语句->' + '~'.join(self.grammar['循环语句'][0])]:
            self.create_node(color=color, label='语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['循环语句'] and '$' in self.first['循环语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # M
    def m(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['M->' + '~'.join(self.grammar['M'][0])]:
            self.create_node(color=color, label='循环语句表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement_table(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['M'] and '$' in self.first['M']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 循环执行语句
    def loop_execute_statement(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][0])]:
            self.create_node(color=color, label='循环用if语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][1])]:
            self.create_node(color=color, label='for语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][2])]:
            self.create_node(color=color, label='循环用if语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][3])]:
            self.create_node(color=color, label='while语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][4])]:
            self.create_node(color=color, label='dowhile语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][5])]:
            self.create_node(color=color, label='return语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][6])]:
            self.create_node(color=color, label='break语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.break_statement(str(self.node_counts)):
                return False

        if self.tokens[self.count] in self.first_candidate['循环执行语句->' + '~'.join(self.grammar['循环执行语句'][7])]:
            self.create_node(color=color, label='continue语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.continue_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['循环执行语句'] and '$' in self.first['循环执行语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # return 语句
    def return_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '121':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='O')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.o(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['return语句'] and '$' in self.first['return语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # for语句
    def for_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '130':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            self.create_node(color=color, label='循环语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['for语句'] and '$' in self.first['for语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # while语句
    def while_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '132':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失)")

            self.create_node(color=color, label='循环语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['while语句'] and '$' in self.first['while语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # dowhile语句
    def dowhile_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '131':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='循环用复合语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_with_statement(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '132':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失while")

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失)")

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")

        elif self.tokens[self.count] in self.follow['while语句'] and '$' in self.first['while语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False
    # 循环用if语句
    def loop_with_if(self, father):
        color = random_color()
        if self.tokens[self.count] == '125':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            self.create_node(color=color, label='循环语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.loop_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='N')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.n(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['循环用if语句'] and '$' in self.first['循环用if语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 循环语句表
    def loop_statement_table(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['循环语句表->' + '~'.join(self.grammar['循环语句表'][0])]:
            self.create_node(color=color, label='循环语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

            self.create_node(color=color, label='M')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.m(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['循环语句表'] and '$' in self.first['循环语句表']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # L
    def l(self, father):
        color = random_color()
        if self.tokens[self.count] == '126':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] in self.follow['L'] and '$' in self.first['L']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # K
    def k(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['K->' + '~'.join(self.grammar['K'][0])]:
            self.create_node(color=color, label='语句表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['K'] and '$' in self.first['K']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # N
    def n(self, father):
        color = random_color()
        if self.tokens[self.count] == '126':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        self.create_node(color=color, label='循环语句')
        self.paint_edge(color=color, father=father, son=str(self.node_counts))
        if not self.loop_statement(str(self.node_counts)):
            return False

        elif self.tokens[self.count] in self.follow['N'] and '$' in self.first['N']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 函数定义形参列表
    def function_definite_formal_parameters_list(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['函数定义形参列表->' + '~'.join(self.grammar['函数定义形参列表'][0])]:
            self.create_node(color=color, label='函数定义形参')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.d(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['函数定义形参列表'] and '$' in self.first['函数定义形参列表']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 函数定义形参
    def function_definite_formal_parameters(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['函数定义形参->' + '~'.join(self.grammar['函数定义形参'][0])]:
            self.create_node(color=color, label='变量类型')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.d(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '700':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失函数名")
                return False

            self.create_node(color=color, label='P')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.p(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['函数定义形参'] and '$' in self.first['函数定义形参']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # P
    def p(self, father):
        color = random_color()
        if self.tokens[self.count] == '304':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='函数定义形参')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definite_formal_parameters(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['P'] and '$' in self.first['P']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # f
    def fa(self, father):
        color = random_color()
        if self.tokens[self.count] == '119':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='常量类型')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant_type(str(self.node_counts)):
                return False

            self.create_node(color=color, label='常量声明表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant_declaration_table(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='i')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ia(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '103':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='i')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ia(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '104':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='i')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ia(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '102':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='i')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ia(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '101':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '700':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失函数名")
                return False

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='函数定义形参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definite_formal_parameters_list(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

            self.create_node(color=color, label='i')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ia(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.first_candidate['f->' + '~'.join(self.grammar['f'][5])]:
            self.create_node(color=color, label='执行语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definition(str(self.node_counts)):
                return False

            self.create_node(color=color, label='i')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ia(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['f'] and '$' in self.first['f']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    def ia(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['i->' + '~'.join(self.grammar['i'][0])]:
            self.create_node(color=color, label='f')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.d(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['i'] and '$' in self.first['i']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # d
    def da(self, father):
        color = random_color()
        if self.tokens[self.count] == '103':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '102':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '104':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] in self.follow['d'] and '$' in self.first['d']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 函数定义
    def function_definition(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['函数定义->' + '~'.join(self.grammar['函数定义'][0])]:
            self.create_node(color=color, label='d')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.da(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '700':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失函数名")
                return False

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='函数定义形参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definite_formal_parameters_list(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            if self.tokens[self.count] == '301':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失{")
                return False

            self.create_node(color=color, label='语句表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.statement_table(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '302':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失}")
                return False

        elif self.tokens[self.count] == '101':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '700':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失函数名")
                return False

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失（")
                return False

            self.create_node(color=color, label='函数定义形参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definite_formal_parameters_list(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）")
                return False

            if self.tokens[self.count] == '301':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失{")
                return False

            self.create_node(color=color, label='f')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.fa(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '302':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失}")
                return False

        elif self.tokens[self.count] in self.follow['函数定义'] and '$' in self.first['函数定义']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 函数块
    def function_block(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['函数块->' + '~'.join(self.grammar['函数块'][0])]:
            self.create_node(color=color, label='函数定义')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_definition(str(self.node_counts)):
                return False

            self.create_node(color=color, label='函数块')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_block(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['函数块'] and '$' in self.first['函数块']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 表达式
    def expression(self, father):
        color = random_color()
        if self.tokens[self.count] == '201':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='算术表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arithmetic_expressions(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("表达式缺失)")
                return False

            self.create_node(color=color, label='B')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.b(str(self.node_counts)):
                return False

            self.create_node(color=color, label='A')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.a(str(self.node_counts)):
                return False

            self.create_node(color=color, label='X')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.x(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.first_candidate['表达式->' + '~'.join(self.grammar['表达式'][1])]:
            self.create_node(color=color, label='常量')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant(str(self.node_counts)):
                return False

            self.create_node(color=color, label='B')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.b(str(self.node_counts)):
                return False

            self.create_node(color=color, label='A')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.a(str(self.node_counts)):
                return False

            self.create_node(color=color, label='X')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.x(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '700':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='Y')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.y(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '205':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='布尔表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_expressions(str(self.node_counts)):
                return False

            self.create_node(color=color, label='E')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.e(str(self.node_counts)):
                return False

            self.create_node(color=color, label='D')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.d(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['表达式'] and '$' in self.first['表达式']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("有错")
            return False

    # 算术表达式
    def arithmetic_expressions(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['算术表达式->' + '~'.join(self.grammar['算术表达式'][0])]:
            self.create_node(color=color, label='项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.item(str(self.node_counts)):
                return False

            self.create_node(color=color, label='A')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.a(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['算术表达式'] and '$' in self.first['算术表达式']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 数值型常量
    def num_constant(self, father):
        color = random_color()
        if self.tokens[self.count] == '400':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1
        elif self.tokens[self.count] == '800':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] in self.follow['数值型常量'] and '$' in self.first['数值型常量']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("缺失数字")
            return False

    # 字符型常量
    def char_constant(self, father):
        color = random_color()
        if self.tokens[self.count] == '500':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] in self.follow['字符型常量'] and '$' in self.first['字符型常量']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("缺失字符")
            return False

    # 常量
    def constant(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['常量' + '~'.join(self.grammar['常量'][0])]:
            self.create_node(color=color, label='数值型常量')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.num_constant(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.first_candidate['常量' + '~'.join(self.grammar['常量'][1])]:
            self.create_node(color=color, label='字符型常量')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.char_constant(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['常量'] and '$' in self.first['常量']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            return False

    # 布尔表达式
    def boolean_expressions(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['布尔表达式' + '~'.join(self.grammar['布尔表达式'][0])]:
            self.create_node(color=color, label='布尔项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_item(str(self.node_counts)):
                return False

            self.create_node(color=color, label='D')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.d(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['布尔表达式'] and '$' in self.first['布尔表达式']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 因子
    def factor(self, father):
        color = random_color()
        if self.tokens[self.count] == '201':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='算术表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arithmetic_expressions(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失）括号")
                return False

        elif self.tokens[self.count] in self.first_candidate['因子' + '~'.join(self.grammar['因子'][1])]:
            self.create_node(color=color, label='常量')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '700':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='V')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.v(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['因子'] and '$' in self.first['因子']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # B
    def b(self, father):
        color = random_color()
        if self.tokens[self.count] == '206':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.item(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '207':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.item(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '208':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.item(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['B'] and '$' in self.first['B']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # A
    def a(self, father):
        color = random_color()
        if self.tokens[self.count] == '209':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='算术表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arithmetic_expressions(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '210':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='算术表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arithmetic_expressions(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['A'] and '$' in self.first['A']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 关系运算符
    def relational_operators(self, father):
        color = random_color()
        if self.tokens[self.count] == '213':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '211':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '214':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '212':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '215':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] == '216':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

        elif self.tokens[self.count] in self.follow['关系运算符'] and '$' in self.first['关系运算符']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 项
    def item(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['项->' + '~'.join(self.grammar['项'][0])]:
            self.create_node(color=color, label='因子')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.factor(str(self.node_counts)):
                return False

            self.create_node(color=color, label='B')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.b(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['项'] and '$' in self.first['项']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    def w(self, father):
        pass

    # X
    def x(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['X->' + '~'.join(self.grammar['X'][0])]:
            self.create_node(color=color, label='关系运算符')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.relational_operators(str(self.node_counts)):
                return False

            self.create_node(color=color, label='项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.item(str(self.node_counts)):
                return False

            self.create_node(color=color, label='A')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.a(str(self.node_counts)):
                return False

            self.create_node(color=color, label='W')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.w(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '217':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='布尔项')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_item(str(self.node_counts)):
                return False

            self.create_node(color=color, label='D')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.d(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '218':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='布尔表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_expressions(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['X'] and '$' in self.first['X']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 布尔因子
    def boolean_factor(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['布尔因子->' + '~'.join(self.grammar['布尔因子'][0])]:
            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['布尔因子'] and '$' in self.first['布尔因子']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("有错")
            return False

    # 布尔项
    def boolean_item(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['布尔项->' + '~'.join(self.grammar['布尔项'][0])]:
            self.create_node(color=color, label='布尔因子')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_factor(str(self.node_counts)):
                return False

            self.create_node(color=color, label='E')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.e(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['布尔项'] and '$' in self.first['布尔项']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("有错")
            return False

    # Y
    def y(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['Y->' + '~'.join(self.grammar['Y'][0])]:
            self.create_node(color=color, label='V')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.v(str(self.node_counts)):
                return False

            self.create_node(color=color, label='B')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.b(str(self.node_counts)):
                return False

            self.create_node(color=color, label='A')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.a(str(self.node_counts)):
                return False

            self.create_node(color=color, label='X')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.x(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '219':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['Y'] and '$' in self.first['Y']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("有错")
            return False

    # 赋值表达式
    def assignment_expression(self, father):
        color = random_color()
        if self.tokens[self.count] == '700':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '219':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("赋值语句缺失=")
                return False

            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['赋值表达式'] and '$' in self.first['赋值表达式']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            return False

    # E
    def e(self, father):
        color = random_color()
        if self.tokens[self.count] == '217':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='布尔表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_expressions(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['E'] and '$' in self.first['E']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # D
    def d(self, father):
        color = random_color()
        if self.tokens[self.count] == '218':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='布尔表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.boolean_expressions(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['D'] and '$' in self.first['D']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # C
    def c(self, father):
        color = random_color()
        if self.tokens[self.count] == '304':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='实参')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arguments(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['C'] and '$' in self.first['C']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 实参
    def arguments(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['实参->' + '~'.join(self.grammar['实参'][0])]:
            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

            self.create_node(color=color, label='C')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.c(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['实参'] and '$' in self.first['实参']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            return False

    # 实参列表
    def arguments_list(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['实参列表->' + '~'.join(self.grammar['实参列表'][0])]:
            self.create_node(color=color, label='实参')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arguments(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['实参列表'] and '$' in self.first['实参列表']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # V
    def v(self, father):
        color = random_color()
        if self.tokens[self.count] == '201':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='实参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.arguments_list(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("main后缺少)")
                return False

        elif self.tokens[self.count] in self.follow['V'] and '$' in self.first['V']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 常量类型
    def constant_type(self, father):
        pass

    # 常量声明表
    def constant_declaration_table(self, father):
        pass

    # T
    def t(self, father):
        color = random_color()
        if self.tokens[self.count] == '219':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='b')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.ba(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['T'] and '$' in self.first['T']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # U
    def u(self, father):
        pass

    # b
    def ba(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['b->' + '~'.join(self.grammar['b'][0])]:
            self.create_node(color=color, label='常量')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.first_candidate['b->' + '~'.join(self.grammar['b'][1])]:
            self.create_node(color=color, label='表达式')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.expression(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['b'] and '$' in self.first['b']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # S
    def s(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['S->' + '~'.join(self.grammar['S'][0])]:
            self.create_node(color=color, label='T')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.t(str(self.node_counts)):
                return False

            self.create_node(color=color, label='U')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.u(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '201':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='函数声明形参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_declared_parameters(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失右括号")
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

        elif self.tokens[self.count] in self.follow['S'] and '$' in self.first['S']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # R
    def r(self, father):
        color = random_color()
        if self.tokens[self.count] == '700':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='S')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.s(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['R'] and '$' in self.first['R']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 声明语句
    def declare_statement(self, father):
        color = random_color()
        if self.tokens[self.count] == '119':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='常量类型')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant_type(str(self.node_counts)):
                return False

            self.create_node(color=color, label='常量声明表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.constant_declaration_table(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '103':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '104':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '102':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            self.create_node(color=color, label='R')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.r(str(self.node_counts)):
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] == '101':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1

            if self.tokens[self.count] == '700':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失函数名字")
                return False

            if self.tokens[self.count] == '201':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失左括号")
                return False

            self.create_node(color=color, label='函数声明形参列表')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.function_declared_parameters(str(self.node_counts)):
                return False

            if self.tokens[self.count] == '202':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失右括号")
                return False

            if self.tokens[self.count] == '303':
                self.create_node(color=color, label=self.sentences[self.count])
                self.paint_edge(color=color, father=father, son=str(self.node_counts))
                self.count += 1
            else:
                print("缺失;")
                return False

            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['声明语句'] and '$' in self.first['声明语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    # 函数声明形参列表
    def function_declared_parameters(self, father):
        pass

    # 执行语句
    def execute_statement(self, father):
        pass

    # 语句
    def statement(self, father):
        color = random_color()
        if self.tokens[self.count] in self.first_candidate['语句->' + '~'.join(self.grammar['语句'][0])]:
            self.create_node(color=color, label='声明语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.declare_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.first_candidate['语句->' + '~'.join(self.grammar['语句'][1])]:
            self.create_node(color=color, label='执行语句')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            if not self.execute_statement(str(self.node_counts)):
                return False

        elif self.tokens[self.count] in self.follow['语句'] and '$' in self.first['语句']:
            self.create_node(color=color, label='$')
            self.paint_edge(color=color, father=father, son=str(self.node_counts))

        else:
            print("error")
            return False

    def ca(self, father):
        color = random_color()
        if self.tokens[self.count] == '133':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1
        else:
            print("程序缺少main函数")
            return False

        if self.tokens[self.count] == '201':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1
        else:
            print("main后缺少(")
            return False

        if self.tokens[self.count] == '202':
            self.create_node(color=color, label=self.sentences[self.count])
            self.paint_edge(color=color, father=father, son=str(self.node_counts))
            self.count += 1
        else:
            print("main后缺少)")
            return False

        self.create_node(color=color, label='复合语句')
        self.paint_edge(color=color, father=father, son=str(self.node_counts))
        if not self.compound_statement(str(self.node_counts)):
            return False

        self.create_node(color=color, label='函数块')
        self.paint_edge(color=color, father=father, son=str(self.node_counts))
        if not self.function_block(str(self.node_counts)):
            return False

    # 程序
    def procedure(self, father):
        color = random_color()
        self.create_node(color=color, label='声明语句')
        self.paint_edge(color=color, father=father, son=str(self.node_counts))
        if not self.declare_statement(str(self.node_counts)):
            return False

        self.create_node(color=color, label='c')
        self.paint_edge(color=color, father=father, son=str(self.node_counts))
        if not self.ca(str(self.node_counts)):
            return False
        return True

    def parser(self):
        self.get_fist()
        self.get_follow()
        if not self.is_ll1():
            return
        self.create_node('red', '程序')
        self.procedure(str(self.node_counts))


def main():
    f = open(r'../../新版编译器测试用例/test2.txt', 'r', encoding='utf-8')
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
        print(sentences)
        x = Recursive(token, sentences)
        x.parser()


if __name__ == '__main__':
    main()
