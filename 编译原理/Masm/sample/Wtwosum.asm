.386 ;��ʾҪ�õ�386ָ��
.model Flat,stdcall ;32λ����Ҫ��flat����;stadcall,��׼����
option casemap:none ;�����Сд

include windows.inc ;�����������ṹ����
include kernel32.inc ;����ԭ������
include user32.inc

includelib kernel32.lib ;�õ��������
includelib user32.lib

.data;������������2���ַ���
szCaption db "5+3����",0
szFive  db    5
szBuffer db 4 dup(0)
.code ;���뿪ʼִ�д�
start: 
    MOV AL,szFive
    ADD AL,3
    ADD AL,30H
    MOV szBuffer,AL  ;��5+3�ĺͷ���szBuffer��������   
     ;����MessageBox API������ʾszBuffer��������8
    invoke MessageBox,NULL,addr szBuffer,addr szCaption,MB_OK 
    invoke ExitProcess,NULL ;�����˳�
end start;����
 

    
   