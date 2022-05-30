;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; 实例11是一个模式对话框程序,使用动态链接库程序.
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
;**************用于定义一个函数指针类型************
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
pFun			PFUN	?		;---定义一个函数指针类型的变量.---
;**************常量******************************
.const 
AppName 			db 	"App1",0 
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
    	.if hLib
    	   	invoke FreeLibrary, hLib
    	.endif
        invoke EndDialog, hWnd,NULL
    .elseif uMsg == WM_COMMAND 
        mov eax, wParam 
        .if ax == IDC_BUTTON_ADD
        	;------------------------------------------------------ 
			; 在得到了动态链接库的句柄后再把您要调用的函数的名称一起
			; 传给GetProcAddress函数.
			; 如果成功的话它:会返回想要的函数的地址，失败的话返回NULL。
			; 除非卸载该动态链接库否则函数的地址是不会改变的，
			; 所以您可以把它保存到一个全局变量中以备后用。 
        	;------------------------------------------------------ 
        	invoke GetProcAddress, hLib , addr szFunctionName1
       		.if eax == NULL 
                invoke MessageBox,NULL,addr FunctionNotFound,addr AppName,MB_OK 
            .else
	        	;----------------------------------------------- 
				; 调用函数时要先把函数的变量压栈，
				; 并且要把包含函数地址信息的变量用方括号括起来。
				; 由于这些函数没有经过原型定义,因此不能使用invoke宏来调用函数.
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
			; 调用LoadLibrary，其参数是欲加载的动态链接库的名称。
			; 如果调用成功，将返回该DLL的句柄。 否则返回NULL。
			; 该句柄可以传给 :library函数和其它需要使用动态链接库句柄的函数。 
        	;-----------------------------------------------  
        	invoke LoadLibrary,addr szLibName 
        	.if eax == NULL 
                invoke MessageBox,NULL,addr DllNotFound,addr AppName,MB_OK 
            .else
            	mov hLib,eax
			.endif 
        .elseif ax == IDC_BUTTON_UNLOAD
        	;-----------------------------------------------  
			; 调用FreeLibrary卸载动态链接库。
        	;-----------------------------------------------  
			invoke FreeLibrary, hLib
			mov hLib, 0 
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
