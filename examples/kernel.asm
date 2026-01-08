;;section .data
db TextAttr,1
db ImportantPorts,1
db Msg,7

;;section .text
label start
    
    ; inicializar puertos importantes
    ivar ImportantPorts,0       ; memoria
    pub 0x4                     ; el video

    ivar Msg,0
    align 0
    pub 6,'f','o','o','b','a','r'

    ; rutina
    sti                         ; hacer interrupciones
    call k_main                 ; llamar al kernel
    call hang                   ; todos los caminos te llevan a hang

label k_main
    ivar Msg,0
    align 0

    mov f,ds
    call print_text

    call hang

; IN f: texto
label print_text

    push ds
    push cycl
    ; registros
    mov ds,f
    align 0
    gub cycl
    call print_text_loop
    pop cycl
    pop ds

    ret

label print_text_loop

    gub c
    call print_char
    loop print_text_loop
    ret

label print_char
    ; guardar
    push c                      ; guardar c
    push ds                     ; guardar data segment
    push off                    ; guardar el offset
    push d                      ; guardar d

    ; puerto
    ivar ImportantPorts,0       ; los puertos
    align 0                     ; 0->ds
    gub d                       ; el puerto

    ; caracter
    out d,c                     ; imprimir
    align 0                     ; off->0
    ivar TextAttr,0             ; ds->&TextAttr
    gub c                       ; c->mem[ds+off]
    out d,c                     ; el dc

    ; recuperar
    pop d                       ; el d
    pop off                     ; el offset
    pop ds                      ; el data segment
    pop c                       ; el caracter

    ret

label hang
    cli
    hlt
    hlt