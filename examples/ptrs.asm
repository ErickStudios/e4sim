; puntero
db PtrToAbc,4
; valor
db Abc,1

call start

; cargar puntero
label load_ptr
    align 0                             ; cargar
    ivar PtrToAbc,0                     ; ivar
    ret

; el inicio
label start
    call load_ptr                       ; cargar
    pul Abc                             ; poner direccion

    call load_ptr                       ; cargar
    gul ds                              ; leer la direccion y setear la direccion actual a la que apunta
    align 0                             ; 0
    mov [byte]2                         ; mover