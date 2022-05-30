import pandas as pd


class FirstFollow:
    def __init__(self, path):
        df = pd.read_csv(path+"test.csv", header=None, encoding='utf-8')
        Nonterm = []

        self.grammer= {}
        for i in range(0, len(df)):
            Nonterm.append(df.iloc[i][0])
            temp = df.iloc[i][1].split("|")
            for pos in range(len(temp)):
                temp[pos] = temp[pos].split(' ')
            self.grammer.update({df.iloc[i][0]: temp})
        self.nonterminal = list(self.grammer.keys())
        self.first = {i: [] for i in self.nonterminal}
        self.follow = {i: [] for i in self.nonterminal}
        self.follow[self.nonterminal[0]].append('#')
        # self.get_all_first()
        # self.get_follow()

    def get_all_first(self):
        def get_first(symbol):
            for procedure_sentence in self.grammer[symbol]:
                # 产生式第一个是终结符
                if procedure_sentence[0] not in self.nonterminal:
                    if procedure_sentence[0] not in self.first[symbol]:
                        self.first[symbol].append(procedure_sentence[0])
                # 产生式的第一个符号是非终结符
                else:
                    while (True):
                        if len(procedure_sentence) == 0:
                            if '$' not in self.first[symbol]:
                                self.first[symbol].append('$')
                            break
                        if procedure_sentence[0] not in self.nonterminal:
                            self.first[symbol].append(procedure_sentence[0])
                            break
                        # 如果当前产生式的第一个非终结符没有first集，先求其first集合
                        if self.first[procedure_sentence[0]] == []:
                            get_first(procedure_sentence[0])
                        if '$' not in self.first[procedure_sentence[0]]:
                            self.first[symbol] += self.first[procedure_sentence[0]]
                            break
                        else:
                            for x in self.first[procedure_sentence[0]]:
                                if x != '$' and x not in self.first[symbol]:
                                    self.first[symbol].append(x)
                            procedure_sentence = procedure_sentence[1:]

        for symbol in self.grammer:
            if self.first[symbol] != []:
                continue
            else:
                get_first(symbol)
        return self.first


    # 获得follow集
    def get_follow(self):
        # 寻找产生式前面的非终结符
        def get_symbol(procedure_sentence):
            for symbol in self.grammer:
                if procedure_sentence in self.grammer[symbol]:
                    return symbol

        # 位于最后一个位置的处理
        def last_place_deal(symbol, procedure_sentence):
            first_symbol = get_symbol(procedure_sentence)
            for follow_symbol in self.follow[first_symbol]:
                if follow_symbol not in self.follow[symbol]:
                    self.follow[symbol].append(follow_symbol)
            # if symbol == '表达式':
            #     print(self.follow[first_symbol], procedure_sentence)

        # 不是最后一个位置, 且后面是非终结符的处理
        def head_place_deal(symbol, procedure_sentence):
            if len(procedure_sentence) == 0:
                return 1
            # 终结符
            if procedure_sentence[0] not in self.nonterminal:
                if procedure_sentence[0] not in self.follow[symbol]:
                    self.follow[symbol].append(procedure_sentence[0])
                return 0
            # 非终结符
            first = self.first[procedure_sentence[0]]
            for x in first:
                if x != '$' and x not in self.follow[symbol]:
                    self.follow[symbol].append(x)
            if '$' in first:
                return head_place_deal(symbol, procedure_sentence[1:])
            else:
                return 0

        # 获得所有产生式
        procedure_sentences = sum(self.grammer.values(), [])

        while (True):
            # 保存本次follow集合内赴澳的数量，判断是否有变化，若没有变化则代表完成，退出即可
            mem = len(sum(self.follow.values(), []))
            # 需要修改的symbol
            for symbol in self.grammer:
                # 判断的产生式
                for procedure_sentence in procedure_sentences:
                    # 产生式里的符号
                    for i in range(len(procedure_sentence)):
                        if procedure_sentence[i] == symbol:
                            # 当前符号在产生式的最后一位
                            if i == len(procedure_sentence) - 1:
                                last_place_deal(symbol, procedure_sentence)
                            # 当前符号的后一位是终结符
                            elif procedure_sentence[i + 1] not in self.nonterminal:
                                if procedure_sentence[i + 1] not in self.follow[symbol]:
                                    self.follow[symbol].append(procedure_sentence[i + 1])
                            # 当前符号的后一位是非终结符
                            else:
                                result = head_place_deal(symbol, procedure_sentence[i + 1:])
                                # result为1时，代表符号后面全是非终结符，且全部能推到空
                                if result == 1:
                                    last_place_deal(symbol, procedure_sentence)
            if len(sum(self.follow.values(), [])) == mem:
                break

        return self.follow