;˵��:��VISTA��Windows 7�����ϵĲ���ϵͳ�»�ͼ����
;�������������WinXP����ģʽ������������
;���÷���������������/ѡ��˵��������ü���
CODES SEGMENT
   ASSUME CS:CODES
START:
  mov ah,00
  mov al,06h
  int 10h ;����640*480��16ɫ��ɫ�ֱ���
  mov dx,50
back_1:
  mov cx,100
back_2:
  mov ah,0ch
  mov al,71h ;�׵���ɫͼ 
  mov bh,0
  int 10h
  inc cx
  cmp cx,200
  jnz back_2
  inc dx
  cmp dx,150
  jnz back_1
CODES ENDS
  END START

