#!/usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd


class OperatorFirstAnalyzer(object):
    def __init__(self, sentences, df):
        self.sentences = sentences
        self.count = 0
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
        self.non_terminator.insert(0, "S")
        for key, value in self.grammar.items():
            for i in value:
                for j in i:
                    if j not in self.terminator and j not in self.non_terminator:
                        self.terminator.append(j)
        self.firstVT = {i: set() for i in self.non_terminator}
        self.lastVT = {i: set() for i in self.non_terminator}
        s = list(self.grammar.keys())[0]
        self.grammar['S'] = [['#', s, '#']]
        self.terminator.append('#')
        self.operator_first_table = pd.DataFrame(columns=list(self.terminator), index=list(self.terminator))
        self.operator_first_table = self.operator_first_table.fillna("")

    def get_firstVT(self):
        stack = []
        # 规则一 p->a...或P->Qa
        for key in self.grammar:
            candidate = self.grammar[key]
            for c in candidate:
                if c[0] in self.terminator:
                    self.firstVT[key].add(c[0])
                    stack.append((key, c[0]))
                elif len(c) >= 2 and c[0] in self.non_terminator and c[1] in self.terminator:
                    self.firstVT[key].add(c[1])
                    stack.append((key, c[1]))
                else:
                    pass
        # 规则二 P->Q... a∈FirstVT(Q),则a∈FirstVT(P)
        # 当堆栈非空,将栈顶元素弹出至(Q,a)。
        # 对每条形如P→Q..的产生式,应用规则2
        while len(stack) > 0:
            element = stack.pop()
            for key in self.grammar:
                candidate = self.grammar[key]
                for c in candidate:
                    if c[0] == element[0]:
                        if element[1] not in self.firstVT[key]:
                            self.firstVT[key].add(element[1])
                            stack.append((key, element[1]))
        print("firstVt: ", self.firstVT)
        f_t = ''
        for key, value in self.firstVT.items():
            f_t += "FIRSTVT(%s) = {%s}\n" % (key, str(value)[1:-1])
        return self.firstVT

    def get_lastVT(self):
        stack = []
        # 规则1: 若有产生式P -..a或P..aQ, 则a∈LastVT(P), 其中P.Q∈Vv, a∈VT。
        for key in self.grammar:
            candidate = self.grammar[key]
            for c in candidate:
                if c[-1] in self.terminator:
                    self.lastVT[key].add(c[-1])
                    stack.append((key, c[-1]))
                elif len(c) >= 2 and c[-1] in self.non_terminator and c[-2] in self.terminator:
                    self.lastVT[key].add(c[-2])
                    stack.append((key, c[-2]))

        # 规则2: 若a∈LastVT(Q), 且有产生式P→...Q, 则a∈LastVT(P)。
        while len(stack) > 0:
            element = stack.pop()
            for key in self.grammar:
                candidate = self.grammar[key]
                for c in candidate:
                    if c[-1] == element[0]:
                        if element[1] not in self.lastVT[key]:
                            self.lastVT[key].add(element[1])
                            stack.append((key, element[1]))
        # print("lastVt: ", self.lastVT)
        return self.lastVT

    def get_operator_first_table(self):
        for key in self.grammar:
            candidate = self.grammar[key]
            for c in candidate:
                for i in range(len(c)):
                    if i + 1 < len(c) and c[i] in self.terminator and c[i + 1] in self.terminator:
                        self.operator_first_table[c[i + 1]][c[i]] = '='
                    if i <= len(c) - 3 and c[i] in self.terminator and c[i + 1] in self.non_terminator and \
                            c[i + 2] in self.terminator:
                        self.operator_first_table[c[i + 2]][c[i]] = '='
                    if i + 1 < len(c) and c[i] in self.terminator and c[i + 1] in self.non_terminator:
                        for a in self.firstVT[c[i + 1]]:
                            self.operator_first_table[a][c[i]] = "<"
                    if i + 1 < len(c) and c[i] in self.non_terminator and c[i + 1] in self.terminator:
                        for a in self.lastVT[c[i]]:
                            self.operator_first_table[c[i + 1]][a] = ">"
        # print("算符优先表：")
        # print(self.operator_first_table, self.operator_first_table.columns)
        return self.operator_first_table, self.operator_first_table.columns
    #
    # def is_reduce(self, c, sub_exp):
    #     if len(c) != len(sub_exp):
    #         return False
    #     for i in range(len(c)):
    #         if (c[i] in self.non_terminator and sub_exp[i] in self.non_terminator) or (
    #                 c[i] in self.terminator and sub_exp[i] in self.terminator and c[i] == sub_exp[i]):
    #             continue
    #         else:
    #             return False
    #     return True

    def is_not_right(self, string):
        for key in self.grammar:
            for c in self.grammar[key]:
                tag = True
                # 如果string长度和right不相同，当然不是，下一个产生式
                if len(c) != len(string):
                    continue
                # 逐个比对c和string的符号
                for ch1, ch2 in zip(c, string):
                    # 如果终结符号与非终结符号类别不相同，不是，下一个产生式
                    if (ch1 in self.terminator and ch2 not in self.terminator) or \
                            (ch1 not in self.terminator and ch2 in self.terminator):
                        tag = False
                        break
                    # 如果是均为终结符号，如果不相同，不是，下一个产生式
                    if ch1 in self.terminator and ch1 != ch2:
                        tag = False
                        break
                # 匹配到某一产生式右部，返回False
                if tag:
                    # print("".join(c))
                    return False
        # 没有匹配到任何一个产生式右部，返回True
        return True

    def analyse(self):
        stack = ['#']
        index = 0
        input_str_stack = [x for x in self.sentences] + ["#"]
        a = input_str_stack[index]
        steps = []
        show_count = 1
        steps.append(["步骤", "栈", "优先关系", "剩余输入串", "移进或规约"])
        while True:
            step = []
            step.append(show_count)
            show_count += 1
            step.append("".join(stack))
            j = -1
            # 始终要对终结符进行比较
            while stack[j] not in self.terminator:
                j -= 1
            # 栈首元素大于输入流元素,则进行归约
            if self.operator_first_table[a][stack[j]] == '>':
                step.append(self.operator_first_table[a][stack[j]])
                # stack = stack[: j + 1] + ['E', ]
                step.append("".join(input_str_stack[index:]))
                step.append("规约")

                while True:
                    temp = stack[j]
                    while True:
                        j -= 1
                        if j >= -len(stack) and stack[j] in self.terminator:
                            break
                    if j < -len(stack) or self.operator_first_table[temp][stack[j]] == '<':
                        break
                if j < -len(stack):
                    print("找不到<关系")
                    return False
                if self.is_not_right(stack[j + 1:]):
                    print("不能匹配任何正确得产生式")
                    return False
                stack = stack[: j + 1] + ['E', ]
                if stack == ['#', 'E'] and a == '#':
                    steps.append(step)
                    step = []
                    step.append(show_count)
                    step.append("".join(stack))
                    step.append('=')
                    step.append("".join(input_str_stack[index:]))
                    step.append("接受")
                    steps.append(step)
                    print(steps)
                    # break
                    return steps
            # 栈首元素大于或等于输入流元素,则把输入流元素压入栈中
            else:
                step.append('<')
                step.append("".join(input_str_stack[index:]))
                step.append("移进")
                if index == len(input_str_stack) - 1:
                    print('不能找到>关系')
                    return False
                stack.append(a)
                index += 1
                a = input_str_stack[index]
                if a not in self.terminator:
                    print("未定义字符")
                    return False
                # print("栈内元素：", stack, "\t", "输入缓冲区：", input_str_stack[index:])
            steps.append(step)

    def run(self):
        self.get_firstVT()
        self.get_lastVT()
        self.get_operator_first_table()
        steps = self.analyse()
        return steps


def main():
    df = pd.read_csv('../data/opt_grammar.csv', encoding='utf-8', header=None)
    sentences = 'i+i*i'
    sentences = list(sentences)
    x = OperatorFirstAnalyzer(sentences, df)
    steps = x.run()
    print("ofa.firstVt: ", x.firstVT)
    print("ofa.lastVt: ", x.lastVT)


if __name__ == '__main__':
    main()
