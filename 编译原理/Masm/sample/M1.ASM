EXTRN   OUTMSG:far			; 说明M2.asm中的子程序OUTMSG
DATAS   SEGMENT      		
MSG	DB 'Hello  ','$'
DATAS   ENDS

CODES	SEGMENT   		
MAIN	PROC FAR
	ASSUME	CS:CODES,DS:DATAS
START:	push	ds
	mov  	ax,0
	push	ax

	mov  	ax,DATAS
	mov  	ds,ax		     	
	mov  	dx,OFFSET MSG     	
	mov  	ah,09h		     	
	int	    21h		     	

	call	far ptr OUTMSG		; 调用M2.asm中的子程序OUTMSG
	ret
MAIN	ENDP
CODES	ENDS
	END START