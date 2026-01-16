; ejemplo de bootsector

db CurrentU32,4

call kmain

label load_byte
    ; cargar byte
    align 0x31                          ; el alineador
    in off,c                            ; el alineado

    ret

label load_dword
    ; cargar el tamaño
    align 8                             ; el alineador comun
    mov f,off                           ; mover alineador

    ; tamaño
    align 0                             ; alinear a 0
    mov d,off                           ; mover

    ; cargar
    call load_byte                      ; cargar
    add d,c                             ; añadir
    shl d,f                             ; shiftear
    call load_byte                      ; cargar
    add d,c                             ; añadir
    shl d,f                             ; shiftear
    call load_byte                      ; cargar
    add d,c                             ; añadir
    shl d,f                             ; shiftear
    call load_byte                      ; cargar
    add d,c                             ; añadir

    ret

label kmain
    ; cargar sector
    align 0                             ; el alinear a 0
    ivar CurrentU32,4                   ; la variable
    pul 512                             ; donde empieza datos validos
    align 0                             ; resetear
    gul b                               ; dato
    align 50                            ; seteador
    out off,b                           ; setear lector

    ; cargar el tamaño del nombre del primer archivo
    call load_dword                     ; cargarlo
    dbg d                               ; imprimir valor
