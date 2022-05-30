;¼ò»¯¶ÎµÄHello World³ÌÐò
.MODEL SMALL
.DATA
     STRING  DB  'Hello World!',13,10,'$'
.STACK
.CODE
.STARTUP
     LEA  DX,STRING
     MOV  AH,9
     INT  21H
.EXIT
     END
