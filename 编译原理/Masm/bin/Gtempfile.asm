.386 ;��ʾҪ�õ�386ָ��
.model Flat,stdcall ;32λ����Ҫ��flat����;stadcall,��׼����
option casemap:none ;�����Сд
include windows.inc ;�����������ṹ����

include kernel32.inc ;����ԭ������
include user32.inc

includelib kernel32.lib ;�õ��������
includelib user32.lib

.data;������������2���ַ���
szText db "Hello world!",0
szCaption db "Masm for Windows ����ʵ�黷��",0

.code ;���뿪ʼִ�д�
start: 
invoke MessageBox,NULL,addr szText,addr szCaption,MB_OK 

;����MessageBoxAPI����
invoke ExitProcess,NULL ;�����˳�
end start;����


