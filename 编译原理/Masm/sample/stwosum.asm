;�򻯶ε���3+5�ĺ�
.MODEL SMALL
.DATA
    FIVE  DB    5

.STACK
      DB  128 DUP (?)
.CODE

.STARTUP
    MOV AL,FIVE
    ADD AL,3
    ADD AL,30H
    MOV DL,AL
    MOV AH,2
    INT 21H
    
.EXIT 0
    END 

