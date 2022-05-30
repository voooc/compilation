import os


class Translate:
    def __init__(self, four, assembly_variable_list):
        self.temp = 0
        self.four = four
        self.assembly_variable_index = 0
        self.assembly_variable_num = 0
        self.assembly_variable_list = assembly_variable_list
        if os.path.exists("Code.txt"):
            os.remove("Code.txt")
        else:
            print("The file does not exist")

    def gen_compilation_code(self, code, index):
        if code[0] == '+':
            # 加法
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nADD AL,{}\nMOV {},AL\n'.format(arg1, arg2, res)

        elif code[0] == '-':
            # 减法
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nSUB AL,{}\nMOV {},AL\n'.format(arg1, arg2, res)

        elif code[0] == '*':
            # 乘法
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nMUL BL\nMOV {},AL\n'.format(arg1, arg2, res)

        elif code[0] == '/':
            # 除法
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AX,{}\nMOV DX,0\nMOV BX,{}\nDIV BX\nMOV {},AL\n'.format(arg1, arg2, res)

        elif code[0] == '%':
            # 求余数
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AX,{}\nMOV DX,0\nMOV AX,{}\nDIV BX\nMOV {},DX\n'.format(arg1, arg2, res)

        elif code[0] == '<':
            # 小于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nCMP AL,BL\nJB _LT{}\nJMP far ptr p{}\n_LT{}:JMP far ptr p{}\n'. \
                format(arg1, arg2, index, str(self.four[index][3] + 1), index, str(code[3] + 1))

        elif code[0] == '>=':
            # 不小于把 res 置为 0， 否则为 1
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nCMP AL,BL\nJA _GE\nJMP far ptr p{}\n_GE:JMP far ptr p{}\n'.format(
                arg1, arg2, str(self.four[index][3] + 1), str(code[3] + 1))

        elif code[0] == '>':
            # 大于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nCMP AL,BL\nJA _GT\nJMP far ptr p{}\n_GT:JMP far ptr p{}\n'.format(
                arg1, arg2, str(self.four[index][3] + 1), str(code[3] + 1))

        elif code[0] == '<=':
            # 不大于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nCMP AL,BL\nJNA _LE\nJMP far ptr p{}\n_LE:JMP far ptr p{}\n'. \
                format(arg1, arg2, str(self.four[index][3] + 1), str(code[3] + 1))

        elif code[0] == '==':
            # 等于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nCMP AL,BL\nJE _EQ\nJMP far ptr p{}\n_EQ:JMP far ptr p{}\n'.format(
                arg1, arg2, str(self.four[index][3] + 1), str(code[3] + 1))

        elif code[0] == '!=':
            # 不等于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV BL,{}\nCMP AL,BL\nJNE _NE\nJMP far ptr p{}\n_NE:JMP far ptr p{}\n'. \
                format(arg1, arg2, str(self.four[index][3] + 1), str(code[3] + 1))

        elif code[0] == '&&':
            # 等于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV DX,0\nMOV AX,{}\nCMP AX,0\nJE _AND\n\tMOV AX,' \
                               '{}\nCMP AX,0\nJE _AND\nMOV DX,1\n_AND:MOV {},DX\n'.format(arg1, arg2, res)

        elif code[0] == '||':
            # A,B有一个未1时，结果为1，否则为0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV DX,1\nMOV AX,{}\nCMP AX,0\nJNE _OR\nMOV AX,{}\nCMP AX,' \
                               '0\nJNE _OR\nMOV DX,0\n_OR:MOV {},DX\n'.format(arg1, arg2, res)

        elif code[0] == '!':
            # A为0时，结果为1，否则为0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV DX,1\nMOV AX,{}\nCMP AX,0\nJE _NOT\nMOV DX,' \
                               '0\n_NOT:MOV {},DX\n'.format(arg1, res)

        elif code[0] == 'j':
            # 无条件跳转到P1
            if self.four[index - 2][0] in ['<', '<=', '>', '>=', '==']:
                return ''
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'JMP far ptr p{}\n'.format(str(res + 1))

        elif code[0] == 'jz':
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nCMP AL,0\nJNE _NE\nJMP far ptr p{}\n_NE:NOP\n'.format(arg1, str(res))

        elif code[0] == 'jnz':
            # 等于把 res 置为 1， 否则为 0
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AX,{}\nCMP AX,0\nJE _EZ\nJMP far ptr p{}\n_EZ:NOP\n'.format(arg1, str(res))

        elif code[0] == 'para':
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AX,{}\nPUSH AX\n'.format(arg1)

        elif code[0] == 'call':
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'CALL {}\n'.format(arg1)

        elif code[0] == 'ret':
            arg1, arg2, res = code[1], code[2], code[3]
            if arg1 != '':
                compilation_code = 'MOV AX,{}\nMOV SP,BP\nPOP BP\nRET\n'.format(arg1)
            else:
                compilation_code = 'MOV SP,BP\nPOP BP\nRET\n'.format(arg1)

        elif code[0] == '=':
            arg1, arg2, res = code[1], code[2], code[3]
            compilation_code = 'MOV AL,{}\nMOV {}, AL\n'.format(arg1, res)

        elif str(code[0]).isidentifier() and code[0] != 'main' and code[0] != 'sys':
            index = code[0]
            compilation_code = 'PUSH BP\nMOV BP,SP\nSUB SP\n'
        else:
            compilation_code = ''
        if compilation_code != '':
            compilation_code = 'p' + str(index) + ':\n' + compilation_code
        return compilation_code

    def generate_compilation_codes(self, start):
        for i, code in enumerate(self.four):
            compilation_code = self.gen_compilation_code(code, i + 1)
            if i == 0:
                compilation_code = start
            elif i == len(self.four) - 1:
                compilation_code = ''
            with open('Code.txt', mode='a+', encoding='utf-8') as f:
                print(compilation_code)
                f.write(compilation_code)

    def generate_variable(self):
        name_stack = []
        value_stack = []
        for i in range(len(self.four)):
            if self.four[i][0] == '=' and self.four[i][3] not in name_stack:
                if isinstance(self.four[i][1], int):
                    name_stack.append(self.four[i][3])
                    value_stack.append(self.four[i][1])
                else:
                    name_stack.append(self.four[i][3])
                    value_stack.append('0')
            elif 'temp' in str(self.four[i][3]) and self.four[i][3] not in name_stack:
                name_stack.append(self.four[i][3])
                value_stack.append('0')
            else:
                pass
        temp = 'assume cs:code,ds:data,ss:stack,es:extended\n\n' \
               'extended segment\n\tdb 1024 dup (0)\nextended ends\n\n' \
               'stack segment\n\tdb 1024 dup (0)\nstack ends\n\n' \
               'data segment\n\tt_buff_p db 256 dup (24h)\n\tt_buff_s db 256 dup (0)\n\tOUTPUT db "Your output is:",' \
               '\'$\'\ndata ends\n\n' \
               'code segment\nstart:mov ax,extended\n\tmov es,ax\n\tmov ax,stack\n\tmov ss,ax\n\tmov sp,1024\n\tmov ' \
               'bp,sp\n\tmov ax,data\n\tmov ds,ax\n\n'
        for i in range(len(value_stack)):
            temp += 'data segment\n' + name_stack[i] + ' db ' + value_stack[i] + '\n' + 'data ends\n' + '\n'
        return temp

    def show(self, variable_name):
        with open('Code.txt', mode='a+', encoding='utf-8') as f:
            end = ('p' + str(len(self.four) + self.assembly_variable_index) + ':')
            print(end)
            f.write('p' + str(len(self.four) + self.assembly_variable_index) + ':')
            f.write('MOV AX,DATA\nMOV DS,AX\nLEA DX,OUTPUT\nMOV AH,09H\nINT 21H\n')
            f.write('MOV al,' + variable_name + '\n')
            f.write('MOV bl,10\nCMP al,bl\n')
            f.write('JA _C' + str(self.assembly_variable_index) + '\n')
            f.write('JMP far ptr pcase' + str(2 * self.assembly_variable_index + 1) + '\n')
            f.write('_C' + str(self.assembly_variable_index) + ':JMP far ptr pcase' + str(
                2 * self.assembly_variable_index + 2) + '\n')
            f.write('pcase' + str(2 * self.assembly_variable_index + 1) + ':ADD ' + variable_name + ',30H\n')
            f.write('MOV DL,' + variable_name + '\n')
            f.write('MOV AH,2\nINT 21H\nMOV DL,0aH\nMOV AH,02H\nINT 21H\n')
            if self.assembly_variable_index < self.assembly_variable_num - 1:
                f.write('JMP far ptr p' + str(len(self.four) + self.assembly_variable_index + 1) + '\n')
            else:
                f.write('JMP far ptr quit\n')
            f.write('\n')
            f.write('pcase' + str(2 * self.assembly_variable_index + 2) + ':mov ax,0\n')
            f.write('ADD AL,' + variable_name + '\n')
            f.write('MOV BL,10\nDIV BL\nMOV DX,AX\nADD DX,3030h\nMOV AH,2\nINT 21H\nMOV DL,DH\nMOV aH,2\n'
                    'INT 21H\nMOV DL,0aH\nMOV AH,02H\nINT 21H\n')
            if self.assembly_variable_index < self.assembly_variable_num - 1:
                f.write('JMP far ptr p' + str(len(self.four) + self.assembly_variable_index + 1) + '\n')
            else:
                f.write('JMP far ptr quit\n')
            f.write('\n')

            self.assembly_variable_index += 1

    def all(self):
        start = self.generate_variable()
        self.generate_compilation_codes(start)
        self.assembly_variable_num = len(self.assembly_variable_list)
        for i in range(self.assembly_variable_num):
            self.show(self.assembly_variable_list[i])
        with open('Code.txt', mode='a+', encoding='utf-8') as f:
            f.write('quit:\nmov ah,4ch\nINT 21H\ncode ends\nend start\n')
