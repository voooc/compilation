assume cs:code,ds:data,ss:stack,es:extended

extended segment
	db 1024 dup (0)
extended ends

stack segment
	db 1024 dup (0)
stack ends

data segment

	t_buff_p db 256 dup (24h)
	t_buff_s db 256 dup (0)
	OUTPUT db "Your output is:",'$'
a db 0
N db 0
M db 0
result db 0
temp2 db 0
data ends


code segment
start:mov ax,extended
	mov es,ax
	mov ax,stack
	mov ss,ax
	mov sp,1024
	mov bp,sp
	mov ax,data
	mov ds,ax



p3:
MOV AL,10
MOV N, AL
p4:
MOV AL,20
MOV M, AL
p5:
MOV AL,M
MOV BL,N
CMP AL,BL
JA _GE
JMP far ptr p9
_GE:JMP far ptr p7
p7:
MOV AL,M
MOV result, AL
p8:
JMP far ptr p10
p9:
MOV AL,N
MOV result, AL
p10:
MOV AL,result
ADD AL,40
MOV temp2,AL
p11:
MOV AL,temp2
MOV a, AL
p12:MOV AX,DATA
MOV DS,AX
LEA DX,OUTPUT
MOV AH,09H
INT 21H
MOV al,result
MOV bl,10
CMP al,bl
JA _C0
JMP far ptr pcase1
_C0:JMP far ptr pcase2
pcase1:ADD result,30H
MOV DL,result
MOV AH,2
INT 21H
MOV DL,0aH
MOV AH,02H
INT 21H
JMP far ptr p13

pcase2:mov ax,0
ADD AL,result
MOV BL,10
DIV BL
MOV DX,AX
ADD DX,3030h
MOV AH,2
INT 21H
MOV DL,DH
MOV aH,2
INT 21H
MOV DL,0aH
MOV AH,02H
INT 21H
JMP far ptr p13

p13:MOV AX,DATA
MOV DS,AX
LEA DX,OUTPUT
MOV AH,09H
INT 21H
MOV al,a
MOV bl,10
CMP al,bl
JA _C1
JMP far ptr pcase3
_C1:JMP far ptr pcase4
pcase3:ADD a,30H
MOV DL,a
MOV AH,2
INT 21H
MOV DL,0aH
MOV AH,02H
INT 21H
JMP far ptr quit

pcase4:mov ax,0
ADD AL,a
MOV BL,10
DIV BL
MOV DX,AX
ADD DX,3030h
MOV AH,2
INT 21H
MOV DL,DH
MOV aH,2
INT 21H
MOV DL,0aH
MOV AH,02H
INT 21H
JMP far ptr quit

quit:
mov ah,4ch
INT 21H
code ends
end start


