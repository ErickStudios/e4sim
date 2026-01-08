; *************************************
; firmware.asm
; *************************************
;
; firmware para el pc Erick4004, este firmware inicializa registros 
; basicos, la pantalla, busca un bootsector en el usb conectado y
; cuando ya no queda mas codigo hace un stub que lee las teclas
;

; para el entero sin signo de 32 bits que se usa en operaciones para
; guardar valores y registros
db CurrentUint32,4
; los puertos importantes para el manejo del i/o basico de cosas como
; el lector usb y el teclado para cuando no queda mas codigo para ejecutar
db ImportantPorts,4
; el buffer del sector de arranque donde contiene los primeros 512 bytes
; del .img que hemos elegido para conectarlo a la usb virtual
db BufferBootSector,512

; llamar el inicio del firmware
call firmware_start

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
    mov [byte]0x20          ; teclado
    mov [byte]0x21          ; esperar tecla
    mov [byte]0x30          ; para resetear el lector
    mov [byte]0x31          ; para leer el lector
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
    call _loadports_        ; cargar puertos
    call init_registers     ; inicializar registros
    call init_screen        ; iniciar pantalla
    ; funciones de rutina
    call boot_sector_read   ; leer el sector
    call key_read           ; leer la tecla
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
    call _loadu32_          ; cargar el u32
    pul 512                 ; los bytes
    align 0                 ; 0->off
    gul cycl                ; ciclos
    ; resetear puerto
    call _getports_         ; obtener puertos
    align 2                 ; el puerto para resetear el lector usb
    gub a                   ; obtener puerto
    out a,b                 ; mandar la señal no importa el valor
    ; buffer
    align 0                 ; 0->ds
    ivar BufferBootSector,0 ; agarrar el buffer de boot sector
    call sector_read_loop   ; leerlo
    ret
label sector_read_loop
    ; obtener el puerto
    call _getports_         ; obtener puertos
    align 3                 ; el puerto para usar el lector usb
    gub a                   ; obtenerlo en a
    in a,b                  ; leerlo
    mov [byte]b             ; ponerlo
    loop sector_read_loop   ; loopear
    ret