#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import pandas as pd
# from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication)
from 编译原理.complier.Gui import Gui, NFAGUI, TranslateGui, Operate
from 编译原理.complier.lexer.NFA_DFA import NfaDfa
from 编译原理.complier.lexer.LeicalAnalysis import LeicalAnalysis
from 编译原理.complier.lexer.AutoLeicalAnalysis import MyLexer
from 编译原理.complier.grammar.recursive_descent import Recursive
from 编译原理.complier.grammar.predict_analyse import PredictAnalyse
from 编译原理.complier.IntermediateCode.middle import Middle
from 编译原理.complier.compilation.translate import Translate
from 编译原理.complier.grammar.operateFirst import OperatorFirstAnalyzer
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class MyWindow(QMainWindow, Gui.Ui_MainWindow):
    def __init__(self):
        self.res = []
        self.error = []
        self.four_code = []
        super(MyWindow, self).__init__()
        self.nfa_window = NFAWindow()
        self.setupUi(self)
        self.actiona.setStatusTip('打开文件')
        self.actiona.triggered.connect(self.show_dialog)
        self.actions_2.setStatusTip('手动词法分析')
        self.actions_2.triggered.connect(self.manual_leical)
        self.actionb.setStatusTip('自动词法分析')
        self.actionb.triggered.connect(self.auto_leical)
        self.actionh.setStatusTip('核心算法')
        self.actionh.triggered.connect(self.show_nfa)

        self.actiona_4.setStatusTip('递归下降')
        self.actiona_4.triggered.connect(self.show_recursive_descent)
        self.actionb_4.setStatusTip('预测分析')
        self.actionb_4.triggered.connect(self.show_predict_analyse)

        self.actiona_3.setStatusTip('递归下降')
        self.actiona_3.triggered.connect(self.show_manual_recursive_descent)
        self.actiong.setStatusTip('预测分析')
        self.actiong.triggered.connect(self.show_manual_predict_analyse)
        self.actionf.setStatusTip('算符优先')
        self.actionf.triggered.connect(self.show_operate_first)

        self.actiona_5.setStatusTip('中间代码')
        self.actiona_5.triggered.connect(self.show_four)
        self.actiond.setStatusTip('目标代码')
        self.actiond.triggered.connect(self.translate)

    def show_dialog(self):
        # 弹出文件选择框。第一个字符串参数是getOpenFileName()方法的标题。第二个字符串参数指定了对话框的工作目录。
        # 默认的，文件过滤器设置成All files (*)。
        f = QFileDialog.getOpenFileName(self, '打开文件', '/home')
        try:
            # 选中文件后，读出文件的内容，并设置成文本编辑框组件的显示文本
            if f[0]:
                f = open(f[0], 'r', encoding='utf-8')
                with f:
                    data = f.read()
                    self.textEdit.setPlainText(data)
        except Exception as e:
            print(e)

    def auto_leical(self):
        try:
            data = self.textEdit.toPlainText()  # 获取文本框内容
            m = MyLexer(data)
            m.build()
            self.res, self.error = m.test()
            self.res.insert(0, '行号' + '\t' + '编码' + '\t' + '单词')
            self.textBrowser.setPlainText('\n'.join(self.res))
            self.error.insert(0, '行号' + '\t' + '错误类型' + '\t' + '单词')
            self.textBrowser_2.setPlainText('\n'.join(self.error))
        except Exception as e:
            print(e)

    def manual_leical(self):
        try:
            data = self.textEdit.toPlainText()  # 获取文本框内容
            l = LeicalAnalysis(data)
            self.res, self.error = l.run()
            self.res.insert(0, '行号' + '\t' + '编码' + '\t' + '单词')
            self.textBrowser.setPlainText('\n'.join(self.res))
            self.error.insert(0, '行号' + '\t' + '错误类型' + '\t' + '单词')
            self.textBrowser_2.setPlainText('\n'.join(self.error))
        except Exception as e:
            print(e)

    def show_nfa(self):
        self.nfa_window.show()

    def show_recursive_descent(self):
        token = []
        sentences = []
        for i in self.res[1:]:
            token.append(i.split('\t')[1])
            sentences.append(i.split('\t')[2])
        if len(token) <= 0:
            print("请输入代码")
        elif len(self.error[1:]) != 0:
            print("语法有错误")
        else:
            df = pd.read_csv('complier/data/grammar - 副本.csv', encoding='utf-8', header=None)
            x = Recursive(token, sentences, df, df[0][0])
            errors = x.parser()
            if errors != '':
                self.textBrowser_2.setPlainText(errors)

    def show_predict_analyse(self):
        token = []
        sentences = []
        for i in self.res[1:]:
            token.append(i.split('\t')[1])
            sentences.append(i.split('\t')[2])
        if len(token) <= 0:
            print("请输入代码")
        elif len(self.error[1:]) != 0:
            print("词法有错误")
        else:
            token.append('#')
            df = pd.read_csv('complier/data/grammar - 副本.csv', encoding='utf-8', header=None)
            x = PredictAnalyse(token, sentences, df)
            res = x.parser()
            self.textBrowser_2.setPlainText(res)

    def show_manual_recursive_descent(self):
        try:
            token = self.textEdit.toPlainText()
            token = list(token)
            del token[-1]
            sentences = token
            df = pd.read_csv('complier/data/small_grammar.csv', encoding='utf-8', header=None)
            x = Recursive(token, sentences, df, df[0][0])
            x.parser()
        except Exception as e:
            print(e)

    def show_manual_predict_analyse(self):
        try:
            token = self.textEdit.toPlainText()
            token = list(token)
            token = ['i', '+', 'i', '*', 'i']
            # del token[-1]
            sentences = token
            token.append('#')
            df = pd.read_csv('complier/data/small_grammar.csv', encoding='utf-8', header=None)
            x = PredictAnalyse(token, sentences, df)
            res = x.parser()
            self.textBrowser_2.setPlainText(res)
        except Exception as e:
            print(e)

    def show_operate_first(self):
        try:
            self.operate_window = OperateFirstWindow()
            self.operate_window.show()
        except Exception as e:
            print(e)

    def show_four(self):
        token = []
        sentences = []
        for i in self.res[1:]:
            token.append(i.split('\t')[1])
            sentences.append(i.split('\t')[2])
        if len(token) <= 0:
            self.textBrowser_2.setPlainText('请输入代码')
            print("请输入代码")
        elif len(self.error[1:]) != 0:
            self.textBrowser_2.setPlainText('词法有错误')
            print("语法有错误")
        else:
            try:
                m = Middle(token, sentences, path='complier/data/')
                m.analyse()
            except Exception as e:
                print(e)
            else:
                if m.errors:
                    self.textBrowser_2.setPlainText(m.errors)
                else:
                    four = []
                    self.four_code = m.gen_code
                    for i in range(len(m.gen_code)):
                        temp = str(i) + '\t' + str(m.gen_code[i])
                        four.append(temp)
                    print('\n'.join(four))
                    self.textBrowser_2.setPlainText('\n'.join(four))

    def translate(self):
        try:
            self.translate_window = TranslateWindow(self.four_code)
            self.translate_window.show()
        except Exception as e:
            print(e)


class NFAWindow(QMainWindow, NFAGUI.Ui_MainWindow):
    def __init__(self):
        super(NFAWindow, self).__init__()
        self.setupUi(self)
        self.temp = None
        self.nfa_nodes = None
        self.dfa_nodes = None
        self.alpha_tab = None
        self.pushButton_2.clicked.connect(self.run_nfa)
        self.pushButton_4.clicked.connect(self.nfa_pic)
        self.pushButton_5.clicked.connect(self.run_dfa)
        self.pushButton_7.clicked.connect(self.dfa_pic)
        self.pushButton_8.clicked.connect(self.run_mdf)
        self.pushButton_10.clicked.connect(self.mdf_pic)

    def run_nfa(self):
        input_str = self.textEdit.toPlainText()
        print(input_str)
        self.s = NfaDfa('complier/data/', input_str)
        alpha_tab = self.s.get_alpha()
        input_str = self.s.regular_modify()
        input_str = self.s.turn_suffix(input_str)
        self.temp, self.nfa_nodes = self.s.convert_nfa(input_str)
        x = self.s.nfa_show_text(self.nfa_nodes)
        self.textBrowser.setPlainText('\n'.join(x))
    def nfa_pic(self):
        self.s.nfa_show(self.temp, self.nfa_nodes)

    def run_dfa(self):
        start_id = self.temp[-1].start.id
        end_id = self.temp[-1].end.id
        self.dfa_nodes = self.s.nfa_to_dfa(self.nfa_nodes, start_id, end_id, self.alpha_tab)
        x = self.s.dfa_show_text(self.dfa_nodes)
        self.textBrowser_2.setPlainText('\n'.join(x))

    def dfa_pic(self):
        self.s.dfa_show(self.dfa_nodes, type='DFA')

    def run_mdf(self):
        self.min_dfa_nodes = self.s.min_dfa(self.dfa_nodes, self.alpha_tab)
        x = self.s.dfa_show_text(self.min_dfa_nodes)
        self.textBrowser_3.setPlainText('\n'.join(x))

    def mdf_pic(self):
        self.s.dfa_show(self.min_dfa_nodes, type='MinDFA')


class TranslateWindow(QMainWindow, TranslateGui.Ui_MainWindow):
    def __init__(self, four_code):
        super(TranslateWindow, self).__init__()
        self.four_code = four_code
        self.setupUi(self)
        self.pushButton.clicked.connect(self.run_translate)

    def run_translate(self):
        input_str = self.textEdit.toPlainText()
        input_str = input_str.split()
        try:
            t = Translate(self.four_code, input_str)
            t.all()
        except Exception as e:
            print(e)


class OperateFirstWindow(QMainWindow, Operate.Ui_MainWindow):
    def __init__(self):
        super(OperateFirstWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.judge_grammar)

    def judge_grammar(self):
        g = self.textEdit.toPlainText()
        isflag, firstvt, lastvt, table, state = '', '', '', '', ''
        try:
            df = pd.read_csv('complier/data/opt_grammar.csv', encoding='utf-8', header=None)
            sentences = 'i+i*i'
            sentences = list(sentences)
            x = OperatorFirstAnalyzer(sentences, df)
            firstVT = x.get_firstVT()
            lastVT = x.get_lastVT()
            operator_first_table, state = x.get_operator_first_table()
            print(state)
        except Exception as e:
            print(e)
        else:
            f_t, l_t, t_t = '', '', ''
            for key, value in firstVT.items():
                f_t += "FIRSTVT(%s) = {%s}\n" % (key, str(value)[1:-1])
            self.textBrowser.setPlainText(f_t)
            for key, value in lastVT.items():
                l_t += "LASTVT(%s) = {%s}\n" % (key, str(value)[1:-1])
            print(l_t)
            self.textBrowser_2.setPlainText(l_t)

            self.tableWidget.setRowCount(len(state))
            self.tableWidget.setColumnCount(len(state))
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tableWidget.resizeColumnToContents(0)

            self.tableWidget.setHorizontalHeaderLabels(state)
            self.tableWidget.setVerticalHeaderLabels(state)

            for i in range(len(state)):
                for j in range(len(state)):
                    v = operator_first_table.iloc[i][j]
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    if i % 2 == 0:
                        item.setBackground(QBrush(QColor(100, 149, 237)))  # 176,196,222
                    else:
                        item.setBackground(QBrush(QColor(176, 196, 222)))
                    self.tableWidget.setItem(i, j, item)
            self.pushButton_2.setEnabled(True)
            input = self.textEdit_2.toPlainText()
            self.pushButton_2.clicked.connect(lambda: self.run_op_first(input))

    def run_op_first(self, input=""):
        df = pd.read_csv('complier/data/opt_grammar.csv', encoding='utf-8', header=None)
        x = OperatorFirstAnalyzer(input, df)
        steps = x.run()
        print(steps)
        self.tableWidget_2.setRowCount(len(steps)-1)
        self.tableWidget_2.setColumnCount(len(steps[0]))
        self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget_2.resizeColumnToContents(0)
        self.tableWidget_2.setHorizontalHeaderLabels(steps[0])
        self.tableWidget_2.verticalHeader().setVisible(False)

        for i in range(1,len(steps)):
            for j in range(len(steps[0])):
                v = steps[i][j]
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                if i % 2 == 0:
                    item.setBackground(QBrush(QColor(100, 149, 237)))
                else:
                    item.setBackground(QBrush(QColor(176, 196, 222)))
                self.tableWidget_2.setItem(i-1, j, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
