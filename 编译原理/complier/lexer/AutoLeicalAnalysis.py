# -*- coding: utf-8 -*-
import 编译原理.complier.ply.lex as lex

key_words = {
        'void': 101, 'char': 102, 'int': 103, 'float': 104, 'double': 105, 'short': 106,
        'long': 107, 'signed': 108, 'unsigned': 109, 'struct': 110, 'union': 111, 'enum': 112,
        'typedef': 113, 'sizeof': 114, 'auto': 115, 'static': 116, 'register': 117, 'extern': 118,
        'const': 119, 'volatile': 120, 'return': 121, 'continue': 122, 'break': 123, 'goto': 124,
        'if': 125, 'else': 126, 'switch': 127, 'case': 128, 'default': 129, 'for': 130, 'do': '131',
        'while': 132
    }


class MyLexer(object):
    def __init__(self, data):
        self.data = data
        self.res = []
        self.error = []

    tokens = (
        '900',
        '700',
        '101',
        '400',
        '800',
        '600',
        '300',
        'octal',
        'hex',
        '500',
        'identifier_error'
    )
    t_400 = r'\d+'
    t_800 = r'([-+]?[0-9]+[.]?[0-9]+([eE])[-+]?[0-9]+)|(0[.]([0-9])+)|([1-9]([0-9])?[.]([0-9])+)'
    t_700 = r'[a-zA-Z_][a-zA-Z_0-9]*'
    t_600 = r'\".+?\"'
    t_500 = r'\'.{1}\''
    t_900 = r'([(\+)(\-)(\*)\(\/)(!)(=)(>)(<)]){1}=|&&|\|\||\+\+|\-\-|\+|-|\*|\/|%|>|<|=|&|\|'
    t_300 = r'\{|\}|\[|\]|\(|\)|,|;|\.|\?|\:|\#'
    t_hex = '0[0-7]+'
    t_octal = '0(x|X)([0-9]|[a-f]|[A-f])+'
    t_ignore_SPECIAL = r'\\t|\\n'
    t_identifier_error = r'(\d)+[a-zA-Z_]+'

    @staticmethod
    def t_newline(t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)
    t_ignore = ' \t'

    @staticmethod
    def t_single_comment(t):
        r"""\/\/.*"""
        cnt = t.value.count('\n')
        t.lexer.lineno += cnt

    @staticmethod
    def t_many_comment(t):
        r"""\/\*(?:[^\*]|\*+[^\/\*])*\*+\/"""
        cnt = t.value.count('\n')
        t.lexer.lineno += cnt

    def t_comment_error(self, t):
        r"""/\*(.|\n)*"""
        self.error.append(str(t.lineno) + '\t' + 'comment error' + '\t' + t.value)

    def t_char_error(self, t):
        r""" (')  [^'\n]* """
        if self.data[self.lexer.lexpos] == "'":
            t.lexer.lexpos += 1
            t.type = '500'
            t.value = self.data[t.lexpos:t.lexer.lexpos]
            return t
        else:
            self.error.append(str(t.lineno) + '\t' + 'char error' + '\t' + t.value[0:t.value.rfind(';')])

    def t_string_error(self, t):
        r""" (")  [^"\n]* """
        if self.data[t.lexer.lexpos] == '"':
            t.lexer.lexpos += 1
            t.type = '600'
            t.value = self.data[t.lexpos:t.lexer.lexpos]
            return t
        else:
            self.error.append(str(t.lineno) + '\t' + 'string error' + '\t' + t.value[0:t.value.rfind(';')])

    def t_zero_error(self, t):
        r"""([0][0-9]+)([0-9]|[.]|e|E)*"""
        if t.value == '0712':
            pass
        else:

            self.error.append(str(t.lineno) + '\t' + 'zero error' + '\t' + t.value)

    def t_hex_error(self, t):
        r"""0(x|X)([0-9]){1}([g-z]|[G-Z])+"""
        self.error.append(str(t.lineno) + '\t' + "hex error" + '\t' + t.value)

    def t_float_error(self, t):
        r"""(0|[1-9]+[0-9]*)[.][^0-9]|(0|[1-9]+[0-9]*)[.]([0-9]+[.][0-9]*)+"""
        self.error.append(str(t.lineno) + '\t' + "float error" + '\t' + t.value)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_error(self, t):
        self.error.append(str(t.lineno) + '\t' + "Illegal character" + '\t' + t.value[0])
        t.lexer.skip(1)

    def test(self):
        self.lexer.input(self.data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            if tok.type == 'many_comment' or tok.type == 'single_comment':
                pass
            else:
                if tok.value in key_words:
                    self.res.append(str(tok.lineno) + '\t' + str(key_words[tok.value]) + '\t' + tok.value)
                elif tok.type == 'identifier_error':
                    self.error.append(str(tok.lineno) + '\t' + tok.type + '\t' + tok.value)
                else:
                    self.res.append(str(tok.lineno) + '\t' + tok.type + '\t' + tok.value)
        return self.res, self.error


if __name__ == '__main__':
    f = open('../data/词法测试.txt', 'r', encoding='utf-8')
    with f:
        data = f.read()
    m = MyLexer(data)
    m.build()
    res, error = m.test()
    res.insert(0, '行号' + '\t' + '编码' + '\t' + '单词')
    print('\n'.join(res))
    error.insert(0, '行号' + '\t' + '错误类型' + '\t' + '单词')
    print('\n'.join(error))
