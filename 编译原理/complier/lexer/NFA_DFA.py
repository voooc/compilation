# coding: utf-8
from graphviz import Digraph
import pandas as pd


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


class NfaNode(object):
    def __init__(self, from_id=None, _id=None, to_id=None, key=chr(949)):
        self.id = _id
        self.key = key
        self.from_id = []
        self.to_id = []

        if from_id is None:
            pass
        elif isinstance(from_id, int):
            self.from_id.append(from_id)
        elif isinstance(from_id, list):
            self.from_id = from_id

        if to_id is None:
            self.to_id = []
        elif isinstance(to_id, int):
            if to_id not in self.to_id:
                self.to_id.append(to_id)
        elif isinstance(to_id, list):
            self.to_id = to_id


class Connection(object):
    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end


class DfaNode(object):
    def __init__(self, number=None, status=None, others=None, is_end=False):
        self.number = number
        self.end_status = is_end
        self.s = list(set(status))
        self.others = others


class NfaDfa(object):
    def __init__(self, path, input_str):
        self.priority_table = pd.read_csv(path + 'priority_table.csv', index_col=0)
        self.regex = input_str

    def regular_modify(self):
        """
        添加.为连接符号
        :param regex:输入的正规式
        :return:调整后的正规式
        """""
        words = []
        for i in range(1, len(self.regex)):
            words.append(self.regex[i - 1])
            if self.regex[i - 1].isalpha() and self.regex[i].isalpha():
                words.append(".")
            elif self.regex[i - 1] == ')' and (self.regex[i].isalpha() or self.regex[i] == '('):
                words.append(".")
            elif self.regex[i - 1] == '*' and (self.regex[i] == '(' or self.regex[i].isalpha()):
                words.append(".")
        words.append(self.regex[len(self.regex) - 1])
        return words

    def turn_suffix(self, regex):
        """
        将正则的中缀转为后缀表达式
        :param regex: 正则
        :return:(a|b)*.a.b.b
        """""
        stack = []
        words = []
        for i in regex:
            if i not in ['*', '|', '.', '(', ')']:
                words.append(i)
            else:
                if i != ')' and (not stack or i == '(' or stack[-1] == '(' or
                                 (self.priority_table.loc[i, stack[-1]] == '>')):
                    stack.append(i)
                elif i == ')':
                    while True:
                        x = stack.pop()
                        if x != '(':
                            words.append(x)
                        else:
                            break
                else:
                    while True:
                        if stack and stack[-1] != '(' and (self.priority_table.loc[i, stack[-1]] == '<' or
                                                           self.priority_table.loc[i, stack[-1]] == '='):
                            words.append(stack.pop())
                        else:
                            stack.append(i)
                            break
        while stack:
            words.append(stack.pop())
        return ''.join(words)

    index = 0

    def alpha_nfa(self, word, status):
        """
        基本符号对应的nfa；
        一个符号由两个节点连接
        :param word: 符号
        :param status: 现存状态
        :return:
        """""
        "两个节点的相联（0-->1）,为0添加指向节点，为1添加来源节点"
        global index
        status.append(NfaNode(None, index, index + 1, word))
        index += 1
        status.append(NfaNode(index - 1, index, None))
        index += 1
        return Connection(start=status[-2], end=status[-1])

    def operator_nfa(self, word, fragments, status):
        """
        操作符转化
        :param word: 操作符
        :param fragments: 操作数栈
        :param status: 状态
        :return: 
        """""
        global index
        if word == '.':
            temp_1, temp_2 = fragments[-2:]
            temp_1.end.to_id.append(temp_2.start.id)
            temp_1.end.key = chr(949)
            temp_2.start.from_id.append(temp_1.end.id)
            fragments.pop()
            fragments.pop()
            return Connection(start=temp_1.start, end=temp_2.end)
        elif word == '|':
            temp_1, temp_2 = fragments[-2:]
            status.append(NfaNode(None, index, [fragment.start.id for fragment in fragments[-2:]], chr(949)))
            temp_1.start.from_id.append(status[-1].id)
            temp_2.start.from_id.append(status[-1].id)
            index += 1
            status.append(NfaNode([fragment.end.id for fragment in fragments[-2:]], index, None, chr(949)))
            temp_1.end.to_id.append(status[-1].id)
            temp_2.end.to_id.append(status[-1].id)
            index += 1
            fragments.pop()
            fragments.pop()
            return Connection(start=status[-2], end=status[-1])
        elif word == '*':
            temp = fragments[-1]
            status.append(NfaNode([temp.end.id], index, None, chr(949)))
            temp.end.to_id.append(index)
            index += 1
            status.append(NfaNode(None, index, [temp.start.id, status[-1].id], chr(949)))
            status[-2].from_id.append(status[-1].id)
            temp.end.to_id.append(temp.start.id)
            temp.start.from_id.append(temp.end.id)
            temp.start.from_id.append(status[-1].id)
            index += 1
            fragments.pop()
            return Connection(start=status[-1], end=status[-2])

    def nfa_show(self, fragments, status):
        """
        :param fragments:结束节点 
        :param status: nfa状态点
        :return: 画图
        """""
        f = Digraph(name="NFA", filename="NFA", format='png')
        f.attr(rankdir='LR', size='8,5')
        f.attr('node', shape='doublecircle')
        f.node('{}'.format(str(fragments[0].end.id)))
        f.attr('node', shape='circle')
        for sta in status:
            for to_id in sta.to_id:
                f.edge("{}".format(str(sta.id)), "{}".format(str(to_id)), label="{}".format(str(sta.key)))
        f.view()

    def nfa_show_text(self, status):
        """
        nfa字体展示
        :param status: nfa状态
        :return: 
        """""
        temp = []
        for sta in status:
            for to_id in sta.to_id:
                temp.append("{}".format(str(sta.id))+'\t'+"{}".format(str(sta.key))+'\t'+ "{}".format(str(to_id)))

        return temp

    def convert_nfa(self, words):
        """
        正规式转化为nfa
        :param words: 修正后的正规式
        :return: 返回初始节点和结束节点、nfa的所有状态节点
        """""
        temp = []
        nfa_status = []
        global index
        index = 0
        for i in range(len(words)):
            if words[i].isalpha():
                temp.append(self.alpha_nfa(words[i], nfa_status))
            else:
                temp.append(self.operator_nfa(words[i], temp, nfa_status))
        "添加一个初始节点"
        nfa_status.append(NfaNode(None, index, temp[-1].start.id, chr(949)))
        temp[-1].start.from_id.append(index)
        temp[-1].start = nfa_status[index]
        index += 1
        return temp, nfa_status

    def closure(self, state, pos, epsilon, closure_list):
        """
        求解闭包
        :param state:状态节点
        :param pos: 当前指向位置
        :param epsilon: e
        :param closure_list: 闭包集合
        :return:
        """""
        if state[pos].key != epsilon:
            return
        else:
            if epsilon == chr(949):
                if pos not in closure_list:
                    closure_list.append(pos)
            for i in state[pos].to_id:
                if i not in closure_list:
                    closure_list.append(i)
                    self.closure(state, i, chr(949), closure_list)
        closure_list.sort()

    def translate_state_new(self, dfa_state):
        """
        重新命名所有的状态，得到一个新的转化表
        :param dfa_state: 
        :return: 
        """""
        for i in range(len(dfa_state)):
            for j in range(len(dfa_state)):
                for k in dfa_state[j].others:
                    if isinstance(dfa_state[j].others[k], list):
                        dfa_state[j].others[k].sort()
                    if isinstance(dfa_state[i].s, list):
                        dfa_state[i].s.sort()
                    if dfa_state[j].others[k] == dfa_state[i].s:
                        dfa_state[j].others[k] = i
        return dfa_state

    def nfa_to_dfa(self, nfa_status, start_state, end_state, alpha_tab):
        """
        nfa转dfa
        :param nfa_status: nfa种的所有状态
        :param start_state: 开始状态
        :param end_state: 结束状态
        :return:
        """""
        pos = 0
        dfa_state = []
        all_state = []
        initial = []
        flag = False
        # 添加首行首列
        self.closure(nfa_status, start_state, chr(949), initial)
        all_state.append(initial)
        # 遍历每行的状态子集
        for single_state in all_state:
            temp = {}
            for k in alpha_tab:
                temp[k] = []
            # 遍历每个状态，计算其closure值
            for j in single_state:
                for k in alpha_tab:
                    self.closure(nfa_status, j, k, temp[k])
            if end_state in single_state:
                flag = True
            dfa_state.append(DfaNode(pos, single_state, temp, flag))
            pos += 1
            for k in alpha_tab:
                if temp[k] and temp[k] not in all_state:
                    all_state.append(temp[k])
        dfa_state = self.translate_state_new(dfa_state)
        return dfa_state

    def dfa_show(self, dfa_nodes, type):
        f = Digraph(name=type, filename=type, format='png')
        f.attr(rankdir='LR', size='8,5')
        f.attr('node', shape='doublecircle')
        for i in range(len(dfa_nodes)):
            if dfa_nodes[i].end_status:
                f.node('{}'.format(str(i)))
        f.attr('node', shape='circle')
        for i in range(len(dfa_nodes)):
            for k in dfa_nodes[i].others:
                if isinstance(dfa_nodes[i].others[k], int):
                    f.edge("{}".format(str(dfa_nodes[i].number)), "{}".format(str(dfa_nodes[i].others[k])), label=k)
        f.view()

    def dfa_show_text(self, dfa_nodes):
        temp = []
        for i in range(len(dfa_nodes)):
            for k in dfa_nodes[i].others:
                if isinstance(dfa_nodes[i].others[k], int):
                    temp.append("{}".format(str(dfa_nodes[i].number))+'\t'+k+'\t'+"{}".
                                format(str(dfa_nodes[i].others[k])))
        return temp

    def get_alpha(self):
        temp = []
        for word in self.regex:
            if word.isalpha():
                temp.append(word)
        return temp

    def get_subset(self, dfa_nodes, node, alpha):
        result = []
        if alpha == '{}'.format(alpha):
            if isinstance(dfa_nodes[node].others[alpha], int) and dfa_nodes[node].others[alpha] not in result:
                result.append(dfa_nodes[node].others[alpha])
        return result

    def divide(self, dfa_nodes, fragment, alpha, result, flag, all):
        if len(fragment) == 1:
            if fragment[0] not in flag:
                result.append(fragment)
                flag.append(fragment[0])
                return
            else:
                return
        subsets = []
        for node in fragment:
            subsets.append(self.get_subset(dfa_nodes, node, alpha))
        t = {}
        temp = []
        for i in range(len(subsets)):
            if subsets[i] not in temp:
                t[str(subsets[i])] = [fragment[i]]
                temp.append(subsets[i])
            else:
                t[str(subsets[i])].append(fragment[i])
        for key, value in t.items():
            # if set(fragment) >= set(value):
            #     # print(fragment)
            #     # print(value)
            #     pass
            # else:
            if len(value) == 1:
                if value[0] not in flag:
                    result.append(value)
                    flag.append(value[0])
                else:
                    pass
            else:
                if value not in all:
                    all.append(value)
                else:
                    pass

    def final_group(self, dfa_nodes, alpha_tab):
        end = []
        no_end =[]
        for i in range(len(dfa_nodes)):
            if dfa_nodes[i].end_status:
                end.append(dfa_nodes[i].number)
            else:
                no_end.append(dfa_nodes[i].number)
        all = [no_end, end]
        result = []
        flag = []
        for alpha in alpha_tab:
            for fragment in all:
                self.divide(dfa_nodes, fragment, alpha, result, flag, all)
                if len(flag) == len(dfa_nodes):
                    break
        temp = []
        for i in range(len(dfa_nodes)):
            if dfa_nodes[i].number not in flag:
                temp.append(i)
                flag.append(i)
        if len(temp) == 0:
            pass
        else:
            result.append(temp)
        return result

    def min_dfa(self, dfa_nodes, alpha_tab):
        result = self.final_group(dfa_nodes, alpha_tab)
        delete_node = []
        for group in result:
            reserve_node = group[0]
            for i in range(1, len(group)):
                delete_node.append(group[i])
                for j in range(len(dfa_nodes)):
                    for k in alpha_tab:
                        if dfa_nodes[j].others[k] == group[i]:
                            dfa_nodes[j].others[k] = dfa_nodes[reserve_node].number
        delete_node.sort(reverse=True)
        for i in range(len(delete_node)):
            del dfa_nodes[delete_node[i]]
        return dfa_nodes


def main():
    # "ab*|b"
    input_str = '(a|b)*'
    input_str = 'ab*|b'
    input_str = "(a|b)*abb"
    s = NfaDfa('../data/', input_str)
    alpha_tab = s.get_alpha()
    input_str = s.regular_modify()
    input_str = s.turn_suffix(input_str)
    # print(input_str)
    temp, nfa_nodes = s.convert_nfa(input_str)
    # nfa_show(temp, nfa_nodes)
    print("regular--------------------------------------------------->nfa")
    x = s.nfa_show_text(nfa_nodes)
    print('\n'.join(x))
    start_id = temp[-1].start.id
    end_id = temp[-1].end.id
    dfa_nodes = s.nfa_to_dfa(nfa_nodes, start_id, end_id, alpha_tab)
    s.dfa_show(dfa_nodes, type='DFA')
    print("nfa----------------------------------------------------------->dfa")
    x = s.dfa_show_text(dfa_nodes)
    print('\n'.join(x))
    min_dfa_nodes = s.min_dfa(dfa_nodes, alpha_tab)
    s.dfa_show(min_dfa_nodes, type='MinDFA')
    print("dfa------------------------------------------------------------->mindfa")
    x = s.dfa_show_text(min_dfa_nodes)
    print('\n'.join(x))


if __name__ == '__main__':
    main()
