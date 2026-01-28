; ********************************
; Tabla de multiplicar del 2
; ********************************

call start

; inicio
label start
    ; el multiplicante
    align 1                             ; multiplicante 1
    mov a,off                           ; mover

    ; llamar
    align 9                             ; el 9
    mov cycl,off                        ; ciclos
    call loop_mul                       ; loop

    cli
    hlt

; loop
label loop_mul
    
    ; ver
    align 2                             ; moverlo
    mul off,a                           ; multiplicar
    dbg off                             ; depurar a la consola serial de logs de python
    inc a                               ; incrementar a

    ; fin
    loop loop_mul                       ; loopear
    ret                                 ; retornar