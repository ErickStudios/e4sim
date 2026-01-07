db PortSolicitud,1

label encender_led
    ; guardar
    push ds                 ; guardar ds
    push off                ; guardar pop

    align 0                 ; off=0
    ivar PortSolicitud,1    ; ds=&PortSolicitud
    pub 1                   ; puerto
    pub 1                   ; dato

    ; datos
    align 0                 ; off=0
    gub a                   ; leer el byte en a
    pub 0                   ; siguiente byte
    gub b                   ; byte actual
    out a,b                 ; enviar

    ; cargar
    pop off                 ; recuperar off
    pop ds                  ; recuperar ds

label apagar_led
    ; guardar
    push ds                 ; guardar ds
    push off                ; guardar pop

    align 0                 ; off=0
    ivar PortSolicitud,1    ; ds=&PortSolicitud
    pub 1                   ; puerto
    pub 0                   ; dato

    ; datos
    align 0                 ; off=0
    gub a                   ; leer el byte en a
    pub 0                   ; siguiente byte
    gub b                   ; byte actual
    out a,b                 ; enviar

    ; cargar
    pop off                 ; recuperar off
    pop ds                  ; recuperar ds