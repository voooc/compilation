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
                # ����ʽ��һ�����ս��
                if procedure_sentence[0] not in self.nonterminal:
                    if procedure_sentence[0] not in self.first[symbol]:
                        self.first[symbol].append(procedure_sentence[0])
                # ����ʽ�ĵ�һ�������Ƿ��ս��
                else:
                    while (True):
                        if len(procedure_sentence) == 0:
                            if '$' not in self.first[symbol]:
                                self.first[symbol].append('$')
                            break
                        if procedure_sentence[0] not in self.nonterminal:
                            self.first[symbol].append(procedure_sentence[0])
                            break
                        # �����ǰ����ʽ�ĵ�һ�����ս��û��first����������first����
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


    # ���follow��
    def get_follow(self):
        # Ѱ�Ҳ���ʽǰ��ķ��ս��
        def get_symbol(procedure_sentence):
            for symbol in self.grammer:
                if procedure_sentence in self.grammer[symbol]:
                    return symbol

        # λ�����һ��λ�õĴ���
        def last_place_deal(symbol, procedure_sentence):
            first_symbol = get_symbol(procedure_sentence)
            for follow_symbol in self.follow[first_symbol]:
                if follow_symbol not in self.follow[symbol]:
                    self.follow[symbol].append(follow_symbol)
            # if symbol == '���ʽ':
            #     print(self.follow[first_symbol], procedure_sentence)

        # �������һ��λ��, �Һ����Ƿ��ս���Ĵ���
        def head_place_deal(symbol, procedure_sentence):
            if len(procedure_sentence) == 0:
                return 1
            # �ս��
            if procedure_sentence[0] not in self.nonterminal:
                if procedure_sentence[0] not in self.follow[symbol]:
                    self.follow[symbol].append(procedure_sentence[0])
                return 0
            # ���ս��
            first = self.first[procedure_sentence[0]]
            for x in first:
                if x != '$' and x not in self.follow[symbol]:
                    self.follow[symbol].append(x)
            if '$' in first:
                return head_place_deal(symbol, procedure_sentence[1:])
            else:
                return 0

        # ������в���ʽ
        procedure_sentences = sum(self.grammer.values(), [])

        while (True):
            # ���汾��follow�����ڸ��ĵ��������ж��Ƿ��б仯����û�б仯�������ɣ��˳�����
            mem = len(sum(self.follow.values(), []))
            # ��Ҫ�޸ĵ�symbol
            for symbol in self.grammer:
                # �жϵĲ���ʽ
                for procedure_sentence in procedure_sentences:
                    # ����ʽ��ķ���
                    for i in range(len(procedure_sentence)):
                        if procedure_sentence[i] == symbol:
                            # ��ǰ�����ڲ���ʽ�����һλ
                            if i == len(procedure_sentence) - 1:
                                last_place_deal(symbol, procedure_sentence)
                            # ��ǰ���ŵĺ�һλ���ս��
                            elif procedure_sentence[i + 1] not in self.nonterminal:
                                if procedure_sentence[i + 1] not in self.follow[symbol]:
                                    self.follow[symbol].append(procedure_sentence[i + 1])
                            # ��ǰ���ŵĺ�һλ�Ƿ��ս��
                            else:
                                result = head_place_deal(symbol, procedure_sentence[i + 1:])
                                # resultΪ1ʱ��������ź���ȫ�Ƿ��ս������ȫ�����Ƶ���
                                if result == 1:
                                    last_place_deal(symbol, procedure_sentence)
            if len(sum(self.follow.values(), [])) == mem:
                break

        return self.follow