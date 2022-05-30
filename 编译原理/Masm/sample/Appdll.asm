;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; 实例10是一个模式对话框程序,该程序调用实例9的动态链接库程序.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
.386 
.model flat, stdcall 
option casemap:none 
;**************头文件和导入库文件****************************
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
;**************常量******************************
.const 
AppName 			db 	"Appdll",0 
szFunctionName2		db	"DecVal",0
szFunctionName1		db	"AddVal",0
szLibName			db	"MyDLL.dll",0 
DllNotFound			db	"The MyDLL.dll could not be found.",0
FunctionNotFound	db	"The Function could not be found.",0
;**************代码段****************************
.code 
DlgProc proc hWnd:HWND, uMsg:UINT, wParam:WPARAM, lParam:LPARAM 
    .if uMsg == WM_INITDIALOG 
        invoke SetDlgItemInt, hWnd, IDC_EDIT, 11, FALSE
    .elseif uMsg == WM_CLOSE 
        invoke EndDialog, hWnd,NULL
    .elseif uMsg == WM_COMMAND 
        mov eax, wParam 
        .if ax == IDC_BUTTON_ADD
        	;---直接调用DLL中的导出函数---
        	invoke AddVal, hWnd, IDC_EDIT
        .elseif ax == IDC_BUTTON_DEC
        	;---直接调用DLL中的导出函数--- 
			invoke DecVal, hWnd, IDC_EDIT
        .endif 
    ;----------------------------------------------- 
    ; 如果送到该对话框过程的消息不是上面这些，
    ; 那么返回FALSE让系统的对话框管理器去处理这些消息,
    ; 否则返回TRUE来告诉系统已经处理过该消息。
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
	; 主程序段,程序的入口处
	;----------------------------------------------- 
    invoke GetModuleHandle, NULL 
    invoke DialogBoxParam, eax, IDD_DIALOG_APP, NULL, DlgProc, NULL 
    invoke ExitProcess, NULL 
	;----------------------------------------------- 
end start 
