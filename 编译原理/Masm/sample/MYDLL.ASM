;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; 该程序是一个简单的动态链接库,用于实现对对话框中
; 的某个值的加减.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; 程序名: MyDll.asm
; Copyright 2004-3 by zhouwei
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
.386 
.model flat,stdcall 
option casemap:none 
;******************include****************************
include 	windows.inc 
include 	user32.inc 
include 	kernel32.inc 
includelib 	user32.lib 
includelib 	kernel32.lib 
;******************data*******************************
.data 
val		dd	?
bRet	dd	?
;******************code******************************
.code 
;================================================================
; 入口函数 
;================================================================
DllEntry proc hInstDLL:HINSTANCE, reason:DWORD, reserved1:DWORD 
	mov  eax,TRUE 
	ret 
DllEntry Endp 
;================================================================
; 下面是两个导出函数，其它程序可以来调用这两个函数。 
;================================================================
AddVal proc hWnd:DWORD, dwID:DWORD
	invoke GetDlgItemInt, hWnd, dwID, NULL, NULL
	inc eax
	invoke SetDlgItemInt, hWnd, dwID, eax, TRUE
    ret 
AddVal endp 
;================================================================
DecVal proc hWnd:DWORD, dwID:DWORD
	invoke GetDlgItemInt, hWnd, dwID, NULL, NULL
	dec eax
	invoke SetDlgItemInt, hWnd, dwID, eax, TRUE
    ret
DecVal endp 

End DllEntry 