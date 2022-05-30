# -*- coding: utf-8 -*-
import pandas as pd
from 编译原理.complier.grammar.first import FirstFollow
from 编译原理.complier.lexer.LeicalAnalysis import LeicalAnalysis


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        temp = self.stack[-1]
        del self.stack[-1]
        return temp

    def top(self):
        temp = self.stack[-1]
        return temp

    def depth(self):
        return len(self.stack)


class Middle:
    def __init__(self, tokens, sentences, path):
        df = pd.read_csv(path+'test.csv', encoding='utf-8', header=None)
        self.sentences = sentences
        self.tokens = tokens
        self.grammar = {}
        self.node_counts = 0
        for i in range(len(df)):
            temp = df.iloc[i][1].split("|")
            res = []
            for j in range(len(temp)):
                res.append(temp[j].split(" "))
            self.grammar.update({df.iloc[i][0]: res})
        temp = FirstFollow(path)
        self.first = temp.get_all_first()
        self.follow = temp.get_follow()
        self.gen_code = []
        self.count = 0
        self.variable_num = 0
        self.errors = ''
        self.constant_table = {}
        self.variable_table = {}
        self.function_table = {}
        self.depth = 1
        self.stack = Stack()
        self.stack.push("0")

    # 声明块
    def declare_block(self):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['声明语句']:
            if not self.declare_statements():
                return False
            return self.declare_block()
        else:
            if str(self.tokens[self.count]) in self.follow['声明块']:
                return True
            else:
                return False

    # 声明语句
    def declare_statements(self):
        try:
            if self.count == len(self.tokens):
                return True
            if self.tokens[self.count] == '119':
                return self.constant_declare()
            elif self.tokens[self.count] in ['103', '104', '102']:
                types = self.sentences[self.count]
                self.count += 1
                if self.tokens[self.count] == '700':
                    self.count += 1
                else:
                    return False
                variable_name = self.sentences[self.count - 1]
                return self.I(types, variable_name)
            elif self.tokens[self.count] == '101':
                types = self.sentences[self.count]
                return self.function_declare(types)
            else:
                return True
        except Exception as e:
            print(e)
            return False

    # 函数声明
    def function_declare(self, types):
        if not self.function_type():
            return False
        if self.tokens[self.count] == '700':
            self.count += 1
            function_name = self.sentences[self.count - 1]
            if function_name not in self.function_table.keys():
                self.function_table.update({function_name: {"type": types,
                                                            "entrance": "/".join(self.stack.stack), "params": [],
                                                            "params_type": []}})
            else:
                self.errors = "函数{}重复定义！".format(function_name)
                return False
        else:
            return False
        if self.tokens[self.count] == '201':
            self.count += 1
        else:
            return False
        if not self.functions_declare_formal_parameters_list(function_name):
            return False
        if self.tokens[self.count] == '202':
            self.count += 1
        else:
            return False
        if self.tokens[self.count] == '303':
            self.count += 1
        else:
            return False
        return True

    # 函数声明形参列表
    def functions_declare_formal_parameters_list(self, function_name):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['函数声明形参']:
            if not self.functions_declare_formal_parameters(function_name):
                return False
            return True
        else:
            if str(self.tokens[self.count]) in self.follow['函数声明形参列表']:
                return True
            else:
                return False

    # 函数声明形参
    def functions_declare_formal_parameters(self, function_name):
        if not self.variable_type(function_name):
            return False
        if not self.J(function_name):
            return False
        return True

    # 变量类型
    def variable_type(self, name):
        if self.tokens[self.count] in ['103', '102', '104']:
            self.count += 1
            parameter_type = self.sentences[self.count - 1]
            self.function_table[name]["params_type"].append(parameter_type)
            return True
        else:
            return False

    # J
    def J(self, name):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] == '304':
            self.count += 1
            if not self.functions_declare_formal_parameters(name):
                return False
            return True
        else:
            return True

    # 函数类型
    def function_type(self):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] in ['103', '102', '104', '101']:
            self.count += 1
            return True
        else:
            return False

    # I
    def I(self, types, name):
        if self.tokens[self.count] == '201':
            if name not in self.function_table.keys():
                entrance = "/".join(self.stack.stack)
                if entrance != '0':
                    self.errors = "{}函数定义位置错误"
                    return False
                self.function_table.update({name: {"return_type": types, "params": [], "params_type": []}})
            else:
                self.errors = "函数{}重复定义！".format(name)
                return False
            self.count += 1
            if not self.functions_declare_formal_parameters(name):
                return False
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False
            return True
        else:
            if not self.F(name):
                return False
            if name not in self.variable_table.keys():
                self.variable_table.update({name: [{"type": types, "entrance": "/".join(self.stack.stack)}]})
            else:
                for i in self.variable_table[name]:
                    if "/".join(self.stack.stack) == i['entrance']:
                        self.errors = "变量{}重复定义！".format(name)
                        return False
                else:
                    self.variable_table[name].append({"type": types, "entrance": "/".join(self.stack.stack)})
            # print(self.sentences[0:self.count])
            # print(self.tokens[self.count])
            if not self.G(types):
                return False
            return True

    # F
    def F(self, name):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] == '219':
            self.count += 1
            expression_result = self.expression()
            if not expression_result[0]:
                return False
            else:
                self.gen_code.append(['=', expression_result[1], '', name])
                return True
        else:
            return True

    # 表达式
    def expression(self):
        if self.tokens[self.count] == '205':
            temp = self.boolean_expression()
            if not temp[0]:
                return False, None
            temp_b = self.B(temp[1])
            if not temp_b[0]:
                return False, None
            temp_a = self.A(temp_b[1])
            if not temp_a[0]:
                return False, None
            return True, temp_a[1]
        else:
            if self.count + 1 < len(self.tokens) and self.tokens[self.count + 1] == '219':
                return self.assignment_expression()
            else:
                temp_arithmetic = self.arithmetic_expression()
                if not temp_arithmetic[0]:
                    return False, None
                temp_d = self.D(temp_arithmetic[1])
                if not temp_d[0]:
                    return False, None
                return True, temp_d[1]

    # A
    def A(self, name):
        if self.count == len(self.tokens):
            return True, name

        if self.tokens[self.count] == '218':
            self.count += 1
            temp_boolean_item = self.boolean_item()
            if temp_boolean_item[0]:
                mid_var = self.get_var_num(1)
                self.gen_code.append(["||", name, temp_boolean_item[1], mid_var])
                return True, mid_var
            else:
                return False, None
        else:
            return True, name

    # 关系表达式
    def relational_expression(self):
        temp_arithmetic_expression = self.arithmetic_expression()
        name = temp_arithmetic_expression[1]
        if not temp_arithmetic_expression[0]:
            return False, None
        if not self.relational_operators():
            return False, None
        sign = self.sentences[self.count - 1]
        temp_arithmetic_expression = self.arithmetic_expression()
        behind_nape = temp_arithmetic_expression[1]
        if not temp_arithmetic_expression[0]:
            return False, None
        mid_var = self.get_var_num(1)
        self.gen_code.append([sign, name, behind_nape, mid_var])
        return True, mid_var

    # D
    def D(self, name):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['关系表达式']:
            if not self.relational_expression():
                return False
            if not self.arithmetic_expression():
                return False
            return True
        elif str(self.tokens[self.count]) in self.first['C']:
            temp_c = self.C(name)
            if not temp_c[0]:
                return False, None
            temp_b = self.B(temp_c[1])
            if not temp_b[0]:
                return False, None
            temp_a = self.A(temp_b[1])
            if not temp_a[0]:
                return False, None
            return True, temp_a[1]
        else:
            if str(self.tokens[self.count]) in self.follow['D']:
                return True, name
            else:
                return False, None

    # B
    def B(self, name):
        if self.count == len(self.tokens):
            return True, name
        if self.tokens[self.count] == '217':
            self.count += 1
            temp_boolean_factor = self.boolean_factor()
            if temp_boolean_factor[0]:
                temp_variable = self.get_var_num(1)
                self.gen_code.append(["&&", name, temp_boolean_factor[1], temp_variable])
                return True, temp_variable
            else:
                return False, None
        else:
            return True, name

    # 布尔表达式
    def boolean_expression(self):
        temp_boolean_item = self.boolean_item()
        if not temp_boolean_item[0]:
            return False, None
        temp_a = self.A(temp_boolean_item[1])
        if not temp_a[0]:
            return False
        return True, temp_a[1]

    # 布尔项
    def boolean_item(self):
        temp_boolean_factor = self.boolean_factor()
        if not temp_boolean_factor[0]:
            return False, None
        temp_b = self.B(temp_boolean_factor[1])
        if not temp_b[0]:
            return False
        return True, temp_b[1]

    # 中间变量
    def get_var_num(self, flag):
        if flag:
            self.variable_num += 1
        return "temp{}".format(self.variable_num)

    # 布尔因子
    def boolean_factor(self):
        if self.tokens[self.count] == '205':
            self.count += 1
            temp_boolean_expression = self.boolean_expression()
            if not temp_boolean_expression[0]:
                return False, None
            else:
                mid_variable = self.get_var_num(1)
                self.gen_code.append(['!', temp_boolean_expression[1], '', mid_variable])
                return True, mid_variable
        else:
            temp_arithmetic_expression = self.arithmetic_expression()
            if not temp_arithmetic_expression[0]:
                return False, None
            temp_c = self.C(temp_arithmetic_expression[1])
            if not temp_c[0]:
                return False
            return True, temp_c[1]

    # 算术表达式
    def arithmetic_expression(self):
        temp_item = self.item()
        if not temp_item[0]:
            return False, None
        temp_x = self.X(temp_item[1])
        if not temp_x[0]:
            return False, None
        return True, temp_x[1]

    # X
    def X(self, name):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['M']:
            temp_m = self.M(name)
            if not temp_m[0]:
                return False, None
            return self.X(temp_m[1])
        else:
            if str(self.tokens[self.count]) in self.follow['X']:
                return True, name
            else:
                return False, None

    # M
    def M(self, name):
        if self.count == len(self.tokens):
            return False
        if self.tokens[self.count] == '209' or self.tokens[self.count] == '210':
            self.count += 1
            sign = self.sentences[self.count - 1]
            temp_item = self.item()
            mid_var = self.get_var_num(1)
            self.gen_code.append([sign, name, temp_item[1], mid_var])
            return temp_item[0], mid_var
        else:
            return False, None

    # 项
    def item(self):
        if self.count == len(self.tokens):
            return False
        temp_factor = self.factor()
        if not temp_factor[0]:
            return False
        temp_y = self.Y(temp_factor[1])
        if not temp_y[0]:
            return False
        return True, temp_y[1]

    # 因子
    def factor(self):
        if self.count == len(self.tokens):
            return False, None
        if self.tokens[self.count] == '201':
            self.count += 1
            temp_arithmetic_expression = self.arithmetic_expression()
            if not temp_arithmetic_expression[0]:
                return False, None
            if self.tokens[self.count] == '202':
                self.count += 1
                return True, temp_arithmetic_expression[1]
            else:
                return False, None
        elif self.tokens[self.count] == '700':
            name = self.sentences[self.count]
            self.count += 1
            if str(self.tokens[self.count]) in self.first['U']:
                if name not in self.function_table.keys():
                    self.errors = "{}函数未定义就直接使用!".format(name)
                    return False, None
                temp_u = self.U(self.sentences[self.count - 1])
                if not temp_u[0]:
                    return False, None
                else:
                    return True, temp_u[1]
            else:
                temp_variable = self.exist_variable(self.sentences[self.count - 1], "/".join(self.stack.stack))
                if not temp_variable:
                    self.errors = "变量{}未定义！".format(self.sentences[self.count - 1])
                    return False, None
                return True, self.sentences[self.count - 1]
        else:
            const_result = self.constant()
            if const_result[0]:
                return True, const_result[1]
            else:
                return False, None

    # 常量
    def constant(self):
        if self.count == len(self.tokens):
            return False, None
        if self.tokens[self.count] == '400' or self.tokens[self.count] == '800' or self.tokens[self.count] == '500':
            self.count += 1
            return True, self.sentences[self.count - 1]
        else:
            return False, None

    def exist_variable(self, name, entrance):
        if name not in self.variable_table.keys():
            return False
        else:
            while len(entrance) >= 1:
                for var in self.variable_table[name]:
                    if var['entrance'] == entrance:
                        return var['entrance']
                entrance = entrance[:-1]
            return False

    # U
    def U(self, name):
        if self.tokens[self.count] == '201':
            self.count += 1
            if not self.arguments_list():
                return False
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False
            temp_variable = self.get_var_num(1)
            self.gen_code.append(['call', name, '', temp_variable])
            return True, temp_variable
        else:
            return False, None

    # 实参
    def arguments(self):
        temp_expression = self.expression()
        if not temp_expression[0]:
            return False
        self.gen_code.append(['para', temp_expression[1], '', ''])
        if not self.E():
            return False
        return True

    # 实参列表
    def arguments_list(self):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['实参']:
            if not self.arguments():
                return False
            return True
        else:
            if str(self.tokens[self.count]) in self.follow['实参列表']:
                return True
            else:
                return False

    # E
    def E(self):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] == '304':
            self.count += 1
            if not self.arguments():
                return False
            return True
        else:
            return True

    # Y
    def Y(self, name):
        if self.count == len(self.tokens):
            return True, None
        if str(self.tokens[self.count]) in self.first['N']:
            temp_n = self.N(name)
            if not temp_n[0]:
                return False, None
            return self.Y(temp_n[1])
        else:
            if str(self.tokens[self.count]) in self.follow['Y']:
                return True, name
            else:
                return False, None

    # N
    def N(self, name):
        if self.count == len(self.tokens):
            return False, None
        if self.tokens[self.count] == '206' or self.tokens[self.count] == '207' or self.tokens[self.count] == '208':
            self.count += 1
            if self.tokens[self.count - 1] == '207' and self.sentences[self.count] == '0':
                self.errors = "除数为0！"
                return False, None
            sign = self.sentences[self.count - 1]
            temp_factor = self.factor()
            if temp_factor[0]:
                temp_variable = self.get_var_num(1)
                self.gen_code.append([sign, name, temp_factor[1], temp_variable])
                return True, temp_variable
            else:
                return False, None
        else:
            return False, None

    # 赋值表达式
    def assignment_expression(self):
        if self.tokens[self.count] == '700':
            self.count += 1
        else:
            return False
        before_nape = self.sentences[self.count - 1]
        if self.tokens[self.count] == '219':
            self.count += 1
        else:
            return False
        temp_expression = self.expression()
        if not temp_expression[0]:
            return False, None
        else:
            self.gen_code.append(['=', temp_expression[1], '', before_nape])
            return temp_expression

    # C
    def C(self, name):
        if self.count == len(self.tokens):
            return True, name
        if str(self.tokens[self.count]) in self.first['关系运算符']:
            if not self.relational_operators():
                return False
            sign = self.sentences[self.count - 1]
            temp_arithmetic_expression = self.arithmetic_expression()
            behind_name = temp_arithmetic_expression[1]
            if not temp_arithmetic_expression[0]:
                return False, None
            mid_var = self.get_var_num(1)
            self.gen_code.append([sign, name, behind_name, mid_var])
            return True, mid_var
        else:
            if str(self.tokens[self.count]) in self.follow['C']:
                return True, name
            else:
                return False, None

    # 关系运算符
    def relational_operators(self):
        if self.tokens[self.count] in ['213', '211', '214', '212', '215', '216']:
            self.count += 1
            return True
        else:
            return False

    # G
    def G(self, types):
        if self.tokens[self.count] == '303':
            self.count += 1
            return True
        else:
            if self.tokens[self.count] == '304':
                self.count += 1
            else:
                return False
            return self.variable_declare_table(types)

    # 变量声明表
    def variable_declare_table(self, types):
        if not self.single_variable_declare(types):
            return False
        return self.G(types)

    # 单变量声明
    def single_variable_declare(self, types):
        if self.tokens[self.count] == '700':
            self.count += 1
        else:
            return False
        name = self.sentences[self.count - 1]
        if name not in self.variable_table.keys():
            self.variable_table.update({name: [{"type": types, "entrance": "/".join(self.stack.stack)}]})
        else:
            for his_information in self.variable_table[name]:
                if "/".join(self.stack.stack) == his_information['path']:
                    self.errors = "变量{}重复定义！".format(name)
                    return False
                else:
                    self.variable_table[name].append({"type": types, "entrance": "/".join(self.stack.stack)})
        return self.F(name)

    # 常量声明
    def constant_declare(self):
        if self.tokens[self.count] == '119':
            self.count += 1
        else:
            return False
        if not self.constant_type():
            return False
        types = self.sentences[self.count - 1]
        if not self.constant_declare_table(types):
            return False
        return True

    # 常量声明表
    def constant_declare_table(self, types):
        if self.tokens[self.count] == '700':
            self.count += 1
        else:
            return False
        const_name = self.sentences[self.count - 1]
        if self.tokens[self.count] == '219':
            self.count += 1
        else:
            return False
        if not self.constant():
            return False
        const_value = self.sentences[self.count - 1]
        const_type = types

        if const_name not in self.constant_table.keys():
            self.constant_table.update(
                {const_name: [{"type": const_type, "value": const_value, "entrance": "/".join(self.stack.stack)}]})
        else:
            for i in self.constant_table[const_name]:
                if "/".join(self.stack.stack) == i['entrance']:
                    self.errors = "常量{}重复定义！".format(const_name)
                    return False
                else:
                    self.constant_table[const_name].append({"type": const_type, "entrance": "/".join(self.stack.stack)})
        if not self.H(types):
            return False
        return True

    # H
    def H(self, types):
        if self.tokens[self.count] == '303':
            self.count += 1
            return True
        else:
            if self.tokens[self.count] == '304':
                self.count += 1
            else:
                return False
            if not self.constant_declare_table(types):
                return False
            return True

    # 常量类型
    def constant_type(self):
        if self.tokens[self.count] in ['103', '102', '104']:
            self.count += 1
            return True
        else:
            return False

    # 复合语句
    def compound_statement(self):
        try:
            if self.tokens[self.count] == '301':
                self.stack.push(str(self.depth))
                self.depth += 1
                self.count += 1
            else:
                return False
            if not self.statement_table():
                return False
            if self.tokens[self.count] == '302':
                self.stack.pop()
                self.count += 1
            else:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    # 语句表
    def statement_table(self):
        if not self.statement():
            return False
        return self.R()

    # 语句
    def statement(self):
        try:
            if self.tokens[self.count] in ['700', '125', '130', '132', '121', '301']:
                return self.execute_statement()
            else:
                return self.declare_statements()
        except Exception as e:
            print(e)
            return False

    # 执行语句
    def execute_statement(self):
        try:
            if self.tokens[self.count] == '700':
                return self.data_processing_statement()
            elif self.tokens[self.count] in ['125', '130', '132', '121']:
                return self.control_statement()
            elif self.tokens[self.count] == '301':
                return self.compound_statement()
            else:
                return False
        except Exception as e:
            print(e)
            return False

    # 数据处理语句
    def data_processing_statement(self):
        try:
            if self.tokens[self.count] == '700':
                self.count += 1
            else:
                return False
            return self.O(self.sentences[self.count - 1])
        except Exception as e:
            print(e)
            return False

    # O
    def O(self, name):
        if self.tokens[self.count] == '219':
            self.count += 1
            temp_expression = self.expression()
            if not temp_expression[0]:
                return False
            self.gen_code.append(['=', temp_expression[1], '', name])
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False
            return True
        elif self.tokens[self.count] == '201':
            self.count += 1
            if not self.arguments_list():
                return False
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False
            self.gen_code.append(['call', name, '', ''])
            return True
        else:
            return False

    # 控制语句
    def control_statement(self):
        try:
            if self.tokens[self.count] == '125':
                return self.if_statement()
            elif self.tokens[self.count] == '130':
                return self.for_statement()
            elif self.tokens[self.count] == '132':
                return self.while_statement()
            elif self.tokens[self.count] == '121':
                return self.return_statement()
            else:
                return False
        except Exception as e:
            print(e)
            return False

    # if语句
    def if_statement(self):
        try:
            if self.tokens[self.count] == '125':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '201':
                self.count += 1
            else:
                return False
            temp_expression = self.expression()
            if not temp_expression[0]:
                return False
            else:
                place = len(self.gen_code) + 1
                self.gen_code[len(self.gen_code)-1][3] = len(self.gen_code)+1
                # self.gen_code.append(['jnz', temp_expression[1], '', len(self.gen_code) + 2])
                self.gen_code.append(['j', '', '', ''])
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False
            if not self.statement():
                return False
            self.gen_code[place-1][3] = len(self.gen_code) + 1
            self.gen_code.append(['j', '', '', ''])
            place = len(self.gen_code) - 1
            temp_p = self.P()
            self.gen_code[place][3] = len(self.gen_code)
            return temp_p
        except Exception as e:
            print(e)
            return False

    # P
    def P(self):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] == '126':
            self.count += 1
            return self.statement()
        else:
            return True

    # for语句
    def for_statement(self):
        try:
            if self.tokens[self.count] == '130':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '201':
                self.count += 1
            else:
                return False
            if not self.expression():
                return False
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False
            temp_expression = self.expression()
            place0 = len(self.gen_code) - 1
            if not temp_expression[0]:
                return False
            else:
                # self.gen_code[len(self.gen_code) - 1][3] = place0
                # self.gen_code.append(['jnz', temp_expression[1], '', ''])
                self.gen_code.append(['j', '', '', ''])
                his_place = len(self.gen_code) - 1

            place1 = len(self.gen_code)
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False

            if not self.expression():
                return False
            self.gen_code.append(['j', '', '', place0])
            # print(self.gen_code)
            # self.gen_code[len(self.gen_code)-1][3] = place0
            self.gen_code[his_place - 1][3] = len(self.gen_code)
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False

            temp_loop_statement = self.loop_statement()
            self.gen_code.append(['j', '', '', place1])

            self.gen_code[his_place][3] = len(self.gen_code)
            return temp_loop_statement
        except Exception as e:
            print(e)
            return False

    # 循环语句
    def loop_statement(self):
        try:
            if self.count == len(self.tokens):
                return True
            if self.tokens[self.count] in ['119', '102', '103', '101', '104']:
                return self.declare_statements()
            elif self.tokens[self.count] in ['125', '130', '132', '121', '123', '122']:
                return self.loop_execute_statement()
            elif self.tokens[self.count] == '301':
                return self.loop_compound_statement()
            elif self.tokens[self.count] == '700':
                return self.data_processing_statement()
            else:
                return True
        except Exception as e:
            print(e)
            return False

    # 循环执行语句
    def loop_execute_statement(self):
        try:
            if self.tokens[self.count] == '125':
                return self.loop_if_statement()
            elif self.tokens[self.count] == '130':
                return self.for_statement()
            elif self.tokens[self.count] == '132':
                return self.while_statement()
            elif self.tokens[self.count] == '121':
                return self.return_statement()
            elif self.tokens[self.count] == '123':
                return self.break_statement()
            elif self.tokens[self.count] == '122':
                return self.continue_statement()
            else:
                return False
        except Exception as e:
            print(e)
            return False

    # break语句
    def break_statement(self):
        try:
            if self.tokens[self.count] == '123':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    # continue语句
    def continue_statement(self):
        try:
            if self.tokens[self.count] == '122':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False
            return True
        except Exception as e:
            print(e)
            return False

    # K
    def K(self):
        if self.tokens[self.count] == '303':
            self.count += 1
            return True, None
        else:
            temp_expression = self.expression()
            if not temp_expression[0]:
                return False
            if self.tokens[self.count] == '303':
                self.count += 1
            else:
                return False, None
            return True, temp_expression[1]

    # 循环if语句
    def loop_if_statement(self):
        try:
            if self.tokens[self.count] == '125':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '201':
                self.count += 1
            else:
                return False
            temp_expression = self.expression()
            if not temp_expression[0]:
                return False
            else:
                place = len(self.gen_code) + 1
                self.gen_code.append(['jnz', temp_expression[1], '', len(self.gen_code) + 2])
                self.gen_code.append(['j', '', '', ''])
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False
            if not self.loop_statement():
                return False
            self.gen_code[place][3] = len(self.gen_code) + 1
            self.gen_code.append(['j', '', '', ''])
            place = len(self.gen_code) - 1
            temp_l = self.L()
            self.gen_code[place][3] = len(self.gen_code)
            return temp_l
        except Exception as e:
            print(e)
            return False

    # L
    def L(self):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] == '126':
            self.count += 1
            return self.loop_statement()
        else:
            return True

    # 循环复合语句
    def loop_compound_statement(self):
        if self.tokens[self.count] == '301':
            self.count += 1
            self.stack.push(str(self.depth))
            self.depth += 1
        else:
            return False

        if not self.loop_statement_table():
            return False

        if self.tokens[self.count] == '302':
            self.count += 1
            self.stack.pop()
        else:
            return False
        return True

    # 循环语句表
    def loop_statement_table(self):
        try:
            if not self.loop_statement():
                return False
            return self.Q()
        except Exception as e:
            print(e)
            return False

    # Q
    def Q(self):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['循环语句表']:
            return self.loop_statement_table()
        else:
            if str(self.tokens[self.count]) in self.follow['Q']:
                return True
            else:
                return False

    # while语句
    def while_statement(self):
        try:
            if self.tokens[self.count] == '132':
                self.count += 1
            else:
                return False
            if self.tokens[self.count] == '201':
                self.count += 1
            else:
                return False
            temp_expression = self.expression()
            if not temp_expression[0]:
                return False
            else:
                place = len(self.gen_code)
                self.gen_code[len(self.gen_code)-1][3] = len(self.gen_code) + 1
                # self.gen_code.append(['jnz', temp_expression[1], '', len(self.gen_code) + 2])
                self.gen_code.append(['j', '', '', ''])
            if self.tokens[self.count] == '202':
                self.count += 1
            else:
                return False
            temp_loop_statement = self.loop_statement()
            self.gen_code[place][3] = len(self.gen_code) + 1
            self.gen_code.append(['j', '', '', place-1])
            return temp_loop_statement
        except Exception as e:
            print(e)
            return False

    # return语句
    def return_statement(self):
        try:
            if self.tokens[self.count] == '121':
                self.count += 1
            else:
                return False
            temp_k = self.K()
            if not temp_k[0]:
                return False
            else:
                self.gen_code.append(['ret', '', '', temp_k[1]])
                return True
        except Exception as e:
            print(e)
            return False

    # R
    def R(self):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['语句表']:
            return self.statement_table()
        else:
            return True

    # 函数块
    def function_block(self):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['函数定义']:
            if not self.function_definitions():
                return False
            return self.function_block()
        else:
            if str(self.tokens[self.count]) in self.follow['函数块']:
                return True
            else:
                return False

    # 函数定义
    def function_definitions(self):
        if not self.function_type():
            return False
        function_type = self.sentences[self.count - 1]
        if self.tokens[self.count] == '700':
            self.count += 1
            self.gen_code.append([self.sentences[self.count - 1], '', '', ''])
        else:
            return False
        function_name = self.sentences[self.count - 1]
        if function_name not in self.function_table.keys():
            self.errors = "{}函数在main函数之前未定义".format(function_name)
            return False
        else:
            types = self.function_table[function_name]['return_type']
            if types != function_type:
                self.errors = "{}函数，其定义函数类型与实际类型不一致".format(function_name)
                return False

        if self.tokens[self.count] == '201':
            self.count += 1
        else:
            return False
        his_type = self.function_table[function_name]['params_type'].copy()
        if not self.function_defines_formal_parameters_list(function_name):
            return False
        types = self.function_table[function_name]['params_type']
        if len(his_type) != int(len(types) / 2):
            self.errors = "{}函数定义参数个数与实际参数个数不同".format(function_name)
        else:
            for i in range(len(his_type)):
                if his_type[i] != types[len(his_type) + i]:
                    self.errors = "{}函数,第个{}参数定义类型为{}，实际类型为{}".format(
                        function_name, i + 1, his_type[i], types[len(his_type) + i])
                    return False
            self.function_table[function_name]['params_type'] = his_type

        if self.tokens[self.count] == '202':
            self.count += 1
        else:
            return False
        if not self.compound_statement():
            return False
        return True

    # 函数定义形参列表
    def function_defines_formal_parameters_list(self, name):
        if self.count == len(self.tokens):
            return True
        if str(self.tokens[self.count]) in self.first['函数定义形参']:
            if not self.function_defines_formal_parameters(name):
                return False
            return True
        else:
            if str(self.tokens[self.count]) in self.follow['函数定义形参列表']:
                return True
            else:
                return False

    # 函数定义形参
    def function_defines_formal_parameters(self, name):
        if not self.variable_type(name):
            return False
        if self.tokens[self.count] == '700':
            types = self.sentences[self.count - 1]
            x = self.sentences[self.count]
            if x not in self.variable_table.keys():
                self.variable_table.update({x: [{"type": types, "entrance": "/".join(self.stack.stack)}]})
            else:
                for his_information in self.variable_table[x]:
                    if "/".join(self.stack.stack) == his_information['path']:
                        self.errors = "变量{}重复定义！".format(x)
                        return False
                    else:
                        self.variable_table[x].append({"type": types, "entrance": "/".join(self.stack.stack)})
            print(self.variable_table)
            self.count += 1
            parameter = self.sentences[self.count - 1]
            self.function_table[name]["params"].append(parameter)
        else:
            return False
        return self.T(name)

    # T
    def T(self, name):
        if self.count == len(self.tokens):
            return True
        if self.tokens[self.count] == '304':
            self.count += 1
            return self.function_defines_formal_parameters(name)
        else:
            return True

    # 程序
    def procedure(self):
        if not self.declare_block():
            return False
        if self.tokens[self.count] == '133':
            self.count += 1
        else:
            return False
        if self.tokens[self.count] == '201':
            self.count += 1
        else:
            return False
        if self.tokens[self.count] == '202':
            self.count += 1
        else:
            return False
        self.gen_code.append(['main', '', '', ''])
        if not self.compound_statement():
            return False
        self.gen_code.append(['sys', '', '', ''])
        if not self.function_block():
            return False
        return True

    def analyse(self):
        result = self.procedure()
        return result


def main():
    f = open(r'../../新版编译器测试用例/test3.txt', 'r', encoding='utf-8')
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
        m = Middle(token, sentences, path='../data/')
        m.analyse()
        print(m.errors)
        print(m.gen_code)


if __name__ == '__main__':
    main()
