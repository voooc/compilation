;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; ʵ��10��һ��ģʽ�Ի������,�ó������ʵ��9�Ķ�̬���ӿ����.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
.386 
.model flat, stdcall 
option casemap:none 
;**************ͷ�ļ��͵�����ļ�****************************
include		windows.inc 
include		user32.inc 
include		kernel32.inc 
includelib 	user32.lib 
includelib 	kernel32.lib 
include 	mydll.inc
includelib 	mydll.lib
;**************equ******************************
IDD_DIALOG_APP		equ	101
IDC_BUTTON_ADD		equ	1000
IDC_BUTTON_DEC		equ	1001
IDC_EDIT			equ	1002
;**************data?****************************
.data? 
hInstance 		HINSTANCE ? 
CommandLine 	LPSTR ? 
buffer 			db 512 dup(?) 
hLib			DWORD	?
dwFunctionAddr	dd	?
;**************����******************************
.const 
AppName 			db 	"Appdll",0 
szFunctionName2		db	"DecVal",0
szFunctionName1		db	"AddVal",0
szLibName			db	"MyDLL.dll",0 
DllNotFound			db	"The MyDLL.dll could not be found.",0
FunctionNotFound	db	"The Function could not be found.",0
;**************�����****************************
.code 
DlgProc proc hWnd:HWND, uMsg:UINT, wParam:WPARAM, lParam:LPARAM 
    .if uMsg == WM_INITDIALOG 
        invoke SetDlgItemInt, hWnd, IDC_EDIT, 11, FALSE
    .elseif uMsg == WM_CLOSE 
        invoke EndDialog, hWnd,NULL
    .elseif uMsg == WM_COMMAND 
        mov eax, wParam 
        .if ax == IDC_BUTTON_ADD
        	;---ֱ�ӵ���DLL�еĵ�������---
        	invoke AddVal, hWnd, IDC_EDIT
        .elseif ax == IDC_BUTTON_DEC
        	;---ֱ�ӵ���DLL�еĵ�������--- 
			invoke DecVal, hWnd, IDC_EDIT
        .endif 
    ;----------------------------------------------- 
    ; ����͵��öԻ�����̵���Ϣ����������Щ��
    ; ��ô����FALSE��ϵͳ�ĶԻ��������ȥ������Щ��Ϣ,
    ; ���򷵻�TRUE������ϵͳ�Ѿ����������Ϣ��
    ;----------------------------------------------- 
    .ELSE 
        mov eax,FALSE 
        ret 
    .ENDIF 
    mov eax,TRUE 
    ret 
DlgProc endp 
;======================================================================
start: 
	;----------------------------------------------- 
	; �������,�������ڴ�
	;----------------------------------------------- 
    invoke GetModuleHandle, NULL 
    invoke DialogBoxParam, eax, IDD_DIALOG_APP, NULL, DlgProc, NULL 
    invoke ExitProcess, NULL 
	;----------------------------------------------- 
end start 
