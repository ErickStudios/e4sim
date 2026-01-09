; *************************************
; firmware/main.asm
; *************************************
;
; firmware para el pc Erick4004, este firmware inicializa registros 
; basicos, la pantalla, busca un bootsector en el usb conectado y
; cuando ya no queda mas codigo hace un stub que lee las teclas
;

; el codigo oem del firmware que es el codigo de el nombre del distribuidor
; del firmware
db FD_OEM,17
; para el entero sin signo de 32 bits que se usa en operaciones para
; guardar valores y registros
db CurrentUint32,4
; los puertos importantes para el manejo del i/o basico de cosas como
; el lector usb y el teclado para cuando no queda mas codigo para ejecutar
db ImportantPorts,7
; el buffer del sector de arranque donde contiene los primeros 512 bytes
; del .img que hemos elegido para conectarlo a la usb virtual
db BufferBootSector,512

; llamar el inicio del firmware
call firmware_start

; setear cycl a 512
label _set_cycl_512_
    ; cargar
    call _loadu32_          ; cargar el u32
    pul 512                 ; los bytes

    ; setear
    align 0                 ; 0->off
    gul cycl                ; ciclos
    ret

; cargar ports
label _getports_
    ivar ImportantPorts,0   ; puertos
    ret

; cargar u32
label _loadu32_
    ; cargar
    align 0                 ; 0->off
    ivar CurrentUint32,4    ; u32 actual
    ret

; inicializar puertos importantes
label _loadports_
    ; inicializar
    align 0                 ; 0->off
    ivar ImportantPorts,0   ; puertos importantes

    ; puertos importantes
    mov [byte]0x20          ; teclado
    mov [byte]0x21          ; esperar tecla
    mov [byte]0x30          ; para resetear el lector
    mov [byte]0x31          ; para leer el lector
    mov [byte]0x40          ; resetea el buffer de ejecucion de codigo externo
    mov [byte]0x41          ; añade un byte a el buffer de ejecucion de codigo externo
    mov [byte]0x42          ; el ejecutor, al escribirse en el ejecuta el codigo del buffer de ejecucion de codigo externo
    ret

; inicializa los registros
label init_registers
    ; inicializar algo
    call _loadu32_          ; cargar
    mov [dword]0            ; setear
    align 0                 ; 0->ds
    gul f                   ; setear a ds

    ; inicializar
    mov a,f                 ; inicializar a
    mov b,f                 ; inicializar b
    mov c,f                 ; inicializar c
    mov d,f                 ; inicializar d
    mov e,f                 ; inicializar e
    mov cycl,f              ; inicializar ciclos
    ret                     ; retornar

; inicializa la pantalla
label init_screen
    ; setear tamaño
    call _loadu32_          ; cargar el u32
    mov [dword]0x7d0        ; poner el u32
    align 0                 ; alinear a 0
    gul cycl                ; tamaño

    ; setear pantalla
    align 0                 ; alinear a 0
    ivar 0xB82,0            ; DS -> video
    loop clear_loop         ; limpiar pantalla
    ret

label clear_loop
    ; llenar
    mov [byte]0x20          ; escribir espacio
    mov [byte]0x07          ; atributo

    loop clear_loop         ; loopear
    ret

; inicializa el firmware
label firmware_start
    ; inicializar
    sti                     ; activar interrupciones
    call init_oem           ; inicializar oem
    call _loadports_        ; cargar puertos
    call init_registers     ; inicializar registros
    call init_screen        ; iniciar pantalla

    ; funciones de rutina
    call boot_sector_read   ; leer el sector

    ; ejecutar el buffer que se leyo
    call load_code          ; cargar el codigo

    ; stub final, loop de teclado
    call key_read           ; leer la tecla

    cli
    hlt

; leer tecla
label key_read
    ; obtener tecla
    hlt                     ; esperar a que algo pase
    align 0                 ; 0->off
    call _getports_         ; obtener puertos
    gub a                   ; donde lo obtiene
    in a,b                  ; ponerlo en c

    ; imprimirla
    align 0                 ; el offset
    ivar 0xB82,0            ; la pantalla
    dbg b
    call key_read           ; tecla

; disk read segment
label boot_sector_read
    ; setear cycl
    call _set_cycl_512_     ; 512->cycl

    ; resetear puerto
    call _getports_         ; obtener puertos
    align 2                 ; el puerto para resetear el lector usb
    gub a                   ; obtener puerto
    out a,b                 ; mandar la señal no importa el valor

    ; buffer
    align 0                 ; 0->ds
    ivar BufferBootSector,0 ; agarrar el buffer de boot sector
    call sector_read_loop   ; leerlo
    dbg a

    ret

label sector_read_loop
    ; guardar
    push ds                 ; guardar el puntero
    push off                ; guardar el offset

    ; obtener el puerto
    call _getports_         ; obtener puertos
    align 3                 ; el puerto para usar el lector usb
    gub a                   ; obtenerlo en a
    in a,b                  ; leerlo

    ; cargar
    pop off                 ; cargar el offset
    pop ds                  ; cargar el puntero

    ; setear
    mov [byte]b             ; ponerlo

    loop sector_read_loop   ; loopear

; cargar codigo
label load_code
    ; obtener el puerto
    call _getports_         ; obtener puertos
    align 4                 ; el puerto para usar el reseteo de codigo ejecutable externo
    gub a                   ; obtenerlo en a
    out a,b                 ; no importa el valor

    ; setear cycl
    call _set_cycl_512_     ; 512->cycl

    ; setear al buffer leido
    align 0                 ; 0->off
    ivar BufferBootSector,0 ; ds->BufferBootSector
    call load_code_loop     ; llamar al loop

; agregar al codigo
label load_code_loop
    ; guardar
    push ds                 ; guardar ds
    push off                ; guardar off

    ; obtener puerto de publicador
    call _getports_         ; obtener puertos
    align 5                 ; el puerto para usar el put byte de codigo ejecutable externo
    gub a                   ; ponerlo

    ; recuperar
    pop off                 ; offset
    pop ds                  ; puntero

    ; obtener byte del sector
    gub b                   ; obtenerlo

    ; mandar dato
    out a,b                 ; mandarlo
    loop load_code_loop     ; loopear
    dbg a

    ; obtener el puerto de ejecucion
    call _getports_         ; obtener puertos
    align 6                 ; obtener el ejecutador
    gub a                   ; guardarlo en a

    ; obtener el puerto de ejecucion
    out a,b                 ; no importa el valor

    ret


; inicializa el oem de el firmware
label init_oem
    align 0
    ivar FD_OEM,17
    mov [byte]'E'           ;.
    mov [byte]'r'           ;.
    mov [byte]'i'           ;.
    mov [byte]'c'           ;.
    mov [byte]'k'           ;.
    mov [byte]'C'           ;.
    mov [byte]'r'           ;.
    mov [byte]'a'           ;.
    mov [byte]'f'           ;.
    mov [byte]'t'           ;.
    mov [byte]'S'           ;.
    mov [byte]'t'           ;.
    mov [byte]'u'           ;.
    mov [byte]'d'           ;.
    mov [byte]'i'           ;.
    mov [byte]'o'           ;.
    mov [byte]'s'           ;.

    ret
