;;section .data

;;section .text
label start

    ; rutina
    sti                         ; hacer interrupciones
    call k_main                 ; llamar al kernel
    call hang                   ; todos los caminos te llevan a hang

label k_main
    ; setear
    ivar 0xB82,0                ; setear ds a la memoria de video
    align 0                     ; setear off a 0

    ; hacer el mensaje
    pub 'h',0x07

label hang
    cli
    hlt
    hlt