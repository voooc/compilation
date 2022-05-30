;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; ʵ��11��һ��ģʽ�Ի������,ʹ�ö�̬���ӿ����.
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
;**************���ڶ���һ������ָ������************
FUNPROTO	typedef proto :DWORD, :DWORD
PFUN		typedef ptr FUNPROTO
;**************equ******************************
IDD_DIALOG_APP		equ	101
IDC_BUTTON_ADD		equ	1000
IDC_BUTTON_DEC		equ	1001
IDC_EDIT			equ	1002
IDC_BUTTON_LOAD		equ	1003
IDC_BUTTON_UNLOAD	equ	1004
;**************data?****************************
.data? 
hInstance 		HINSTANCE ? 
CommandLine 	LPSTR ? 
buffer 			db 512 dup(?) 
hLib			DWORD	?
dwFunctionAddr	dd	?
pFun			PFUN	?		;---����һ������ָ�����͵ı���.---
;**************����******************************
.const 
AppName 			db 	"App1",0 
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
    	.if hLib
    	   	invoke FreeLibrary, hLib
    	.endif
        invoke EndDialog, hWnd,NULL
    .elseif uMsg == WM_COMMAND 
        mov eax, wParam 
        .if ax == IDC_BUTTON_ADD
        	;------------------------------------------------------ 
			; �ڵõ��˶�̬���ӿ�ľ�����ٰ���Ҫ���õĺ���������һ��
			; ����GetProcAddress����.
			; ����ɹ��Ļ���:�᷵����Ҫ�ĺ����ĵ�ַ��ʧ�ܵĻ�����NULL��
			; ����ж�ظö�̬���ӿ�������ĵ�ַ�ǲ���ı�ģ�
			; ���������԰������浽һ��ȫ�ֱ������Ա����á� 
        	;------------------------------------------------------ 
        	invoke GetProcAddress, hLib , addr szFunctionName1
       		.if eax == NULL 
                invoke MessageBox,NULL,addr FunctionNotFound,addr AppName,MB_OK 
            .else
	        	;----------------------------------------------- 
				; ���ú���ʱҪ�ȰѺ����ı���ѹջ��
				; ����Ҫ�Ѱ���������ַ��Ϣ�ı����÷�������������
				; ������Щ����û�о���ԭ�Ͷ���,��˲���ʹ��invoke�������ú���.
	        	;----------------------------------------------- 
            	mov dwFunctionAddr,eax 
            	push IDC_EDIT
            	push hWnd
            	call [dwFunctionAddr] 
            .endif
        .elseif ax == IDC_BUTTON_DEC 
        	invoke GetProcAddress,hLib,addr szFunctionName2
       		.if eax == NULL 
                invoke MessageBox,NULL,addr FunctionNotFound,addr AppName,MB_OK 
            .else
            	mov pFun, eax 
            	invoke pFun, hWnd, IDC_EDIT
            .endif
        .elseif ax == IDC_BUTTON_LOAD
        	;-----------------------------------------------  
			; ����LoadLibrary��������������صĶ�̬���ӿ�����ơ�
			; ������óɹ��������ظ�DLL�ľ���� ���򷵻�NULL��
			; �þ�����Դ��� :library������������Ҫʹ�ö�̬���ӿ����ĺ����� 
        	;-----------------------------------------------  
        	invoke LoadLibrary,addr szLibName 
        	.if eax == NULL 
                invoke MessageBox,NULL,addr DllNotFound,addr AppName,MB_OK 
            .else
            	mov hLib,eax
			.endif 
        .elseif ax == IDC_BUTTON_UNLOAD
        	;-----------------------------------------------  
			; ����FreeLibraryж�ض�̬���ӿ⡣
        	;-----------------------------------------------  
			invoke FreeLibrary, hLib
			mov hLib, 0 
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
