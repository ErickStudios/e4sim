; *************************************
; firmware/main.asm
; *************************************
;
; firmware para el pc Erick4004, este firmware inicializa registros 
; basicos, la pantalla, busca un bootsector en el usb conectado y
; cuando ya no queda mas codigo hace un stub que lee las teclas
;

; sector de arranque
stru BootSector {
    ; tamaño de header
    .hdrSize db 1

    ; nombre del fs
    .fsName db 8
    ; nombre del vendor
    .vendorName db 7

    ; donde inician los datos
    .datas db 496
}

; el codigo oem del firmware que es el codigo de el nombre del distribuidor
; del firmware
db FD_OEM,17
; para el entero sin signo de 32 bits que se usa en operaciones para
; guardar valores y registros
db CurrentUint32,4
; los puertos importantes para el manejo del i/o basico de cosas como
; el lector usb y el teclado para cuando no queda mas codigo para ejecutar,
; para guardar el codigo del firmware en memoria
db ImportantPorts,10

; el buffer del sector de arranque donde contiene los primeros 512 bytes
; del .img que hemos elegido para conectarlo a la usb virtual
imp BootSector at BufferBootSector

; la linea actual de la pantalla en modo texto para que la linea se guarde
db VgaCurrentRow,4
; la colummna actual de la pantalla en modo texto para que la linea se guarde
db VgaCurrentCol,4
; el actual caracter en prompt
db PromptCurrChar,4

; donde termina la pantalla
org e4asm.mapend

db MySelf,24320

ivar BufferBootSector,0
dbg ds

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
    mov [byte]0x50          ; el guardador de memoria
    mov [byte]0x51          ; el puerto para setear el numero de interrupcion
    mov [byte]0x52          ; el puerto para setear el offset al numero de interrupcion elegida
    mov [byte]0x54          ; el seteador de tamaño del idt
    mov [byte]0x55          ; el puerto que devuelve el tamaño de myself
    mov [byte]0x32          ; para setear el lector
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

    ; funciones de llamado
    call memory_idt_load    ; cargar el idt

    ; funciones de rutina
    call boot_sector_read   ; leer el sector

    ; ejecutar el buffer que se leyo
    call load_code          ; cargar el codigo

    cli
    hlt

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
    gub a                   ; obtenerlo
    mov off,a               ; añadir al offset
    sub cycl,a              ; menos ciclos

    call load_code_loop     ; llamar al loop

    ret

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

    ; obtener el puerto de ejecucion
    call _getports_         ; obtener puertos
    align 6                 ; obtener el ejecutador
    gub a                   ; guardarlo en a

    ; obtener el puerto de ejecucion
    out a,b                 ; no importa el valor

    call hang_bugs          ; llamar a el manejador de bugs para continuar por que si hago ret se bugea y salta a codigo arbitrario

; prueba de interrupcion
label int_disk
    ; guardar
    push ds                 ; guardar ds
    push off                ; guardar off
    push a                  ; guardar b

    align 0x32              ; el offset
    out off,a               ; setear

    ; cargar
    pop a                   ; cargar b
    pop off                 ; cargar off
    pop ds                  ; cargar ds
    iret

; para guardar el idt
label memory_idt_load
    ; setear tamaño del int
    call _getports_         ; obtener los puertos
    align 10                ; el id del seteador de tamaño del idt
    gub a                   ; guardarlo
    call _getports_         ; obtener los puertos
    align 11                ; el id del obtencion del tamaño de myself
    gub d                   ; obtenerlo
    in d,c                  ; obtenerlo
    out a,c                 ; setearlo

    ; obtener datos
    call _getports_         ; obtener los puertos
    align 7                 ; el id
    gub a                   ; guardarlo

    ; guardar direccion de memoria
    call _loadu32_          ; cargar u32
    pul MySelf              ; guardar direccion
    align 0                 ; off->0
    gul b                   ; guardar en b

    ; llamar al puerto
    out a,b                 ; a es el puerto, b es la direccion donde lo guardara

    ; cargar puerto de seteo de interrupciones
    call _getports_         ; obtener los puertos
    align 8                 ; el id
    gub a                   ; guardarlo
    call _loadu32_          ; cargar el u32
    pub 0                   ; setear a 0
    align 0                 ; off->0
    gub b                   ; cargar en b
    out a,b                 ; resetear el contador

    ; int de disco
    call inc_and_add_idt    ; setear address
    call _getports_         ; obtener puertos
    align 9                 ; puerto id 9
    gub a                   ; setear a
    call _loadu32_          ; cargar u32
    pul int_disk            ; cargar la direccion de la funcion dentro del codigo
    align 0                 ; off->0
    gul b                   ; el offset
    out a,b                 ; setear int
    ret
; para añadir e incrementar las interrupciones
label inc_and_add_idt
    ; guardar
    push a                  ; guardar a
    push ds                 ; guardar ds
    push off                ; guardar off

    ; obtener puerto
    call _getports_         ; obtener puertos
    align 8                 ; el puerto 8
    gub a                   ; guardar en a
    out a,f                 ; enviar

    ; siguiente
    inc f                   ; incrementar

    ; cargar
    pop off                 ; cargar off
    pop ds                  ; cargar ds
    pop a                   ; recuperar a
    ret
; para manejar el bug
label hang_bugs
label end
    cli
    hlt

; inicializa el oem de el firmware
label init_oem
    ; cargar el oem
    align 0                 ; 0->off
    ivar FD_OEM,17          ; ds->FD_OEM

    ; OEM label
    pub 'E','r','i','c','k','C','r','a','f','t','S','t','u','d','i','o','s'

    ret
