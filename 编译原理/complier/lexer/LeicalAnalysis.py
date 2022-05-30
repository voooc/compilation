# -*- coding: utf-8 -*-
class LeicalAnalysis:
    def __init__(self, text):
        self.text = text
        self.key_words = {
            'void': 101, 'char': 102, 'int': 103, 'float': 104, 'double': 105, 'short': 106,
            'long': 107, 'signed': 108, 'unsigned': 109, 'struct': 110, 'union': 111, 'enum': 112,
            'typedef': 113, 'sizeof': 114, 'auto': 115, 'static': 116, 'register': 117, 'extern': 118,
            'const': 119, 'volatile': 120, 'return': 121, 'continue': 122, 'break': 123, 'goto': 124,
            'if': 125, 'else': 126, 'switch': 127, 'case': 128, 'default': 129, 'for': 130, 'do': '131',
            'while': 132, 'main': 133
        }
        self.bor_sign = {
            '{': 301, '}': 302, ';': 303, ',': 304, '"': 305, '#': 306
        }
        self.cal_sign = {
            '(': 201, ')': 202, '[': 203, ']': 204, '!': 205, '*': 206,  '/': 207, '%': 208,
            '+': 209, '-': 210, '<': 211, '<=': 212, '>': 213, '>=': 214, '==': 215, '!=': 216,
            '&&': 217, '||': 218, '=': 219, '.': 220, '&': 221, '|': 222, '++': 223, '--': 224,
            '+=': 225, '-=': 226, '*=': 227, '/=': 228, '&=': 229, '^=': 230, '|=': 231, '%=': 232,
            '>>=': 233, '<<=': 234, '>>': 235, '<<': 236
        }
        self.rows = 1
        self.p = 0

    def run(self):
        """
        运行函数
        1.去掉无用的换行符以及注释等
        2.将剩余字符变成列表后尾部添加"\0"
        3.识别字符
        :return:
        """""
        words = list(self.text)
        words = self.filter(words)
        words.append('\n')
        words, err = self.identify(words)
        return words, err

    def identify(self, words):
        """
        识别整个列表中的字符，将单个单词和其对应的类别存进列表中125
        :param words: 整个列表
        :return: 单词对应的类别
        """""
        output = []
        err = []
        words.append('\0')
        while self.p < len(words):
            if words[self.p] == "\0":
                break
            x1, x2 = self.check(words)
            temp_output1 = ','.join(x1)
            temp_output2 = ','.join(x2)
            if temp_output1 == '':
                pass
            else:
                output.append(temp_output1 + '\t')
            if temp_output2 == '':
                pass
            else:
                err.append(temp_output2 + '\t')
        return output, err

    def get_char(self, words):
        """
        提取下一个字符
        :param words: 整个列表
        :return:
        """""
        ch = words[self.p]
        if ch == '\n':
            self.rows += 1
        self.p += 1
        return ch

    def get_blank_ch(self, ch, words):
        """
        跳过空白符直至ch读入一个非空白符
        :param ch:当前字符
        :param words:整个列表
        :return:
        """""
        while ch == ' ':
            ch = self.get_char(words)
        return ch

    def check(self, words):
        """
        依次检查每个字符
        :param words:所有的字符列表
        :return:单词以及其对应的种类
        result为单词以及其对应的种类
        temp_words为单个单词
        ch为单个字符
        """""
        result = []
        error = []
        temp_words = []
        ch = self.get_char(words)
        ch = self.get_blank_ch(ch, words)
        """
        识别标识符
        1.判断首字母是否为字母或者下划线(将首字母放入temp_words中)
        2.获取下一个字符
        3.循环获取下一个字符直到下一个字符不是字母/数字/下划线(将字母放入temp_words中)
        4.回退道上一个字符
        5.将temp_words变成字符串，判断是否在关键字列表中
        """""
        # 识别标识符
        if ch.isalpha() or ch == '_':
            temp_words.append(ch)
            ch = self.get_char(words)
            while ch.isalpha() or ch.isdigit() or ch == '_':
                temp_words.append(ch)
                ch = self.get_char(words)
            self.retract(words)
            temp = ''.join(temp_words)
            if temp in self.key_words:
                result.append(str(self.rows)+'\t'+str(self.key_words[temp])+'\t'+temp)
                return result, error
            else:
                result.append(str(self.rows)+'\t'+'700'+'\t'+temp+'\t')
                return result, error
        # 识别数值型常数
        elif ch.isdigit():
            if int(ch) == 0:
                state = 3
            else:
                state = 1
            temp_words.append(ch)
            ch = self.get_char(words)
            if ch == '.':
                if state == 3:
                    state = 8
            if state != 3:
                while ch.isdigit():
                    temp_words.append(ch)
                    ch = self.get_char(words)
                if ch == '.' or state == 8:
                    temp_words.append(ch)
                    ch = self.get_char(words)
                    if ch.isdigit():
                        temp_words.append(ch)
                        state = 9
                    else:
                        state = 16
                elif ch == 'E' or ch == 'e':
                    temp_words.append(ch)
                    state = 10
                elif ch == ' ' or ch in self.bor_sign or ch in self.cal_sign or ch == '\n':
                    state = 15
                else:
                    state = 16
                if state == 9:
                    ch = self.get_char(words)
                    if ch.isdigit():
                        while ch.isdigit():
                            temp_words.append(ch)
                            ch = self.get_char(words)
                    if ch == 'E' or ch == 'e':
                        temp_words.append(ch)
                        state = 10
                    elif ch == ' ' or ch in self.bor_sign or ch in self.cal_sign or ch == '\n':
                        if ch != '.':
                            state = 14
                        else:
                            state = 16
                    else:
                        state = 16
                if state == 10:
                    ch = self.get_char(words)
                    if ch.isdigit():
                        temp_words.append(ch)
                        state = 12
                    elif ch == '+' or ch == '-':
                        temp_words.append(ch)
                        state = 11
                    else:
                        state = 16
                if state == 11:
                    ch = self.get_char(words)
                    temp_words.append(ch)
                    if ch.isdigit():
                        state = 12
                    else:
                        state = 16
                if state == 12:
                    ch = self.get_char(words)
                    if ch.isdigit():
                        while ch.isdigit():
                            temp_words.append(ch)
                            ch = self.get_char(words)
                    if ch == ' ' or ch in self.bor_sign or ch in self.cal_sign or ch == '\n':
                        self.retract(words)
                        state = 13
                    else:
                        state = 16
            else:
                if ch.isdigit():
                    if 0 <= int(ch) <= 7:
                        while ch.isdigit():
                            if 0 <= int(ch) <= 7:
                                temp_words.append(ch)
                                ch = self.get_char(words)
                        state = 4
                        if ch == '.':
                            state = 16
                    else:
                        temp_words.append(ch)
                        ch = self.get_char(words)
                        while 1:
                            if ch == ' ' or ch in self.bor_sign or ch in self.cal_sign or ch == '\n':
                                break
                            else:
                                temp_words.append(ch)
                                ch = self.get_char(words)
                        state = 16
                elif ch == 'x' or ch == 'X':
                    # state = 5
                    temp_words.append(ch)
                    ch = self.get_char(words)
                    if ch.isdigit() or ('a' <= ch <= 'f') or ('A' <= ch <= 'F'):
                        temp_words.append(ch)
                        ch = self.get_char(words)
                        if ch.isdigit() or ('a' <= ch <= 'f') or ('A' <= ch <= 'F'):
                            temp_words.append(ch)
                            state = 7
                        else:
                            temp_words.append(ch)
                            state = 16
                    else:
                        state = 16
                    ch = self.get_char(words)
                elif ch == ' ' or ch in self.bor_sign or ch in self.cal_sign or ch == '\n':
                    state = 15
            temp = ''.join(temp_words)
            if state == 15:
                self.retract(words)
                result.append(str(self.rows)+'\t'+'400' + '\t' + str(temp)+'\t')
            elif state == 4:
                result.append(str(self.rows)+'\t'+'octal' + '\t' + str(temp)+'\t')
            elif state == 7:
                result.append(str(self.rows)+'\t'+'hex' + '\t' + str(temp)+'\t')
            elif state == 16:
                value = ch
                while 1:
                    if value == 'e' or value == 'E':
                        if ch == '+' or ch == '-':
                            pass
                    elif ch != '.' and (ch in self.bor_sign or ch == ' ' or ch in self.cal_sign or ch == '\n'):
                        break
                    value = ch
                    temp_words.append(ch)
                    ch = self.get_char(words)
                temp = ''.join(temp_words)
                error.append(str(self.rows)+'\t'+'num error' + '\t' + str(temp)+'\t')
            else:
                result.append(str(self.rows)+'\t'+'800' + '\t' + str(temp)+'\t')
            return result, error
        # 识别字符常数
        elif ch == "'":
            temp_words.append(ch)
            ch = self.get_char(words)
            if ch == '\\':
                temp_words.append(ch)
                ch = self.get_char(words)
            temp_words.append(ch)
            ch = self.get_char(words)
            if ch == "'":
                temp_words.append(ch)
                temp = ''.join(temp_words)
                result.append(str(self.rows)+'\t'+'500' + '\t' + str(temp))
            else:
                temp = ''.join(temp_words)
                self.retract(words)
                error.append(str(self.rows)+'\t'+'char error' + '\t' + str(temp))
            return result, error
        # 识别字符串常数
        elif ch == '"':
            temp_words.append(ch)
            ch = self.get_char(words)
            flag = False
            while ch != '"':
                temp_words.append(ch)
                ch = self.get_char(words)
                if words[self.p] == "\n":
                    flag = True
                    break
            temp_words.append(ch)
            temp = ''.join(temp_words)
            if flag:
                error.append(str(self.rows)+'\t'+'字符串出错' + '\t' + temp+'\t')
            else:
                result.append(str(self.rows)+'\t'+'600' + '\t' + temp+'\t')
            return result, error
        # 识别运算符
        elif ch in self.cal_sign:
            value = ch
            ch = self.get_char(words)
            if ch == '/' and value == '/':
                temp_words.append(value)
                while 1:
                    if ch != '\n':
                        temp_words.append(ch)
                        ch = self.get_char(words)
                    else:
                        break
                temp = ''.join(temp_words)
                result.append(str(self.rows) + '\t' + '10000' + '\t' + temp + '\t')
                return '', ''
            elif value == '/' and ch == '*':
                temp_words.append(value)
                temp_words.append(ch)
                value = self.get_char(words)
                flag = False
                temp_words.append(value)
                while 1:
                    try:
                        if value != '*' or ch != '/':
                            self.retract(words)
                            value = self.get_char(words)
                            ch = self.get_char(words)
                            temp_words.append(ch)
                        else:
                            break
                    except Exception as e:
                        print(e)
                        break
                    if words[self.p] == "\0":
                        flag = True
                        break
                if flag:
                    error.append(str(self.rows)+'\t'+'非法注释' + '\t')
                    return '', error
                else:
                    temp = ''.join(temp_words)
                    # result.append(str(self.rows) + '\t' + '10000' + '\t' + temp + '\t')
                    return '', ''
            if ch in self.cal_sign:
                value += ch
                while 1:
                    if value in self.cal_sign and ch in self.cal_sign:
                        ch = self.get_char(words)
                        value += ch
                    else:
                        break
                self.retract(words)
                temp = value[:-1]
                result.append(str(self.rows)+'\t'+str(self.cal_sign[temp]) + '\t' + temp)
                return result, error
            else:
                temp = ''.join(value)
                self.retract(words)
                result.append(str(self.rows)+'\t'+str(self.cal_sign[temp]) + '\t' + temp)
                return result, error
        # 识别界符
        elif ch in self.bor_sign:
            temp = ''.join(ch)
            result.append(str(self.rows)+'\t'+str(self.bor_sign[temp]) + '\t' + temp)
            return result, error
        else:
            if ch == '\n':
                return '', ''
            else:
                while 1:
                    if ch in self.bor_sign or ch == ' ' or ch in self.cal_sign or ch == '\n':
                        break
                    else:
                        temp_words.append(ch)
                        ch = self.get_char(words)
                temp = ''.join(temp_words)
                error.append(str(self.rows)+'\t'+'Illegal character' + '\t' + temp)
                return result, error

    def retract(self, words):
        """
        将字符的指向回到上一个位置
        :return:
        """""
        self.p -= 1
        if words[self.p] == '\n':
            self.rows -= 1
        return

    @staticmethod
    def filter(sentences):
        """
        去除\t
        :param sentences: 所有字符的列表形式
        :return: 剩余字符的字符串形式
        """""
        temp_sentences = []
        i = 0
        while i < len(sentences):
            if sentences[i] != '\t':
                temp_sentences.append(sentences[i])
            i += 1
        return temp_sentences
