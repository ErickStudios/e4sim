; ejemplo de bootsector

db CurrentU32,4

; ponerlo donde termina el display ya que mas alla es memoria libre por ahora en
; la version actual cuando se escribio este codigo, asi que es seguro, mientras
; el stack no se pase de listo, no habra problemas
org e4asm.mapend

; tamaño del archivo
db FileSize,4
; contenido del archivo, este puede ser mas grande ya que la direccion en la que
; esta es segura de expandir
db FileContent,4096

call kmain

; activa el modo protegido
label protect_mode_activate
    ; pasos
    push cycl                           ; guardar cycl
    mov ds,ds                           ; confirmar ds
    push a                              ; guardar a para no perder su valor
    gub a                               ; obtener el byte al que apunta (ds+off)
    dec off                             ; ir al byte anterior para ponerlo
    mov [byte]a                         ; no cambia nada por que setea el mismo valor
    inc cycl                            ; incrementar cycl para que se pueda hacerse el jmp
    loop protected_mode_entry           ; entrar a modo protegido

; entrada
label protected_mode_entry
    ; recuperar para obtener el ret
    pop a                               ; los recupera
    pop cycl                            ; los recupera

    ret

; carga un byte desde la usb
label load_byte
    ; cargar byte
    align 0x31                          ; el alineador
    in off,c                            ; el alineado

    ret

; carga un u32 desde la usb
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

; principal
label kmain
    ; cargar sector
    align 0                             ; el alinear a 0
    ivar CurrentU32,4                   ; la variable
    pul 512                             ; donde empieza datos validos

    ; cargar
    align 0                             ; resetear
    gul b                               ; dato
    align 50                            ; seteador
    mov e,off                           ; copiarlo al e
    out off,b                           ; setear lector

    call read_file                      ; llamar a read file

    ; loop
    cli                                 ; desactivar
    hlt                                 ; haltear
    hlt                                 ; haltear
    call end

label read_file
    ; leer
    call reset_program_buffer           ; resetear buffer de programa
    call skip_name                      ; salta el nombre
    call read_content                   ; leer contenido
    call loop_read                      ; loopear
    ret

label skip_name
    ; cargar el tamaño del nombre del primer archivo
    call load_dword                     ; cargarlo

    ; añadirlo
    in e,a                              ; obtener el usbindex
    add a,d                             ; añadirlo

    ; cargar valor en el puerto
    align 50                            ; seteador
    mov e,off                           ; copiarlo al e

    ; setearlo
    out e,a                             ; setear index
    ret

label read_content
    ; cargar el tamaño del contenido del archivo
    call load_dword                     ; dword
    ivar FileSize,0                     ; setear a filesize
    align 0                             ; off->0
    mov d                               ; copiar el valor
    mov cycl,d                          ; mover ciclo a d
    ivar 0xBB2,0                        ; a la pantalla
    align 0                             ; alinear a 0

    ret

label reset_program_buffer
    ; resetear el programa
    align 0x40                          ; el puerto
    mov a,off                           ; copiar off a a
    out a,b                             ; outpear a
    ret

label loop_read
    ; guardar
    push ds                             ; guardar ds
    push off                            ; guardar off

    ; cargar byte
    call load_byte                      ; cargar
    align 0x41                          ; puerto
    out off,c                           ; offset

    ; recuperar
    pop off                             ; recuperar off
    pop ds                              ; recuperar ds

    ; fin
    loop loop_read                      ; loopear
    call protect_mode_activate          ; activar modo protegido
    align 66                            ; puerto
    out off,a                           ; alinear

    call end

label end