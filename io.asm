
; puertos
db Port1,1              ; puerto secundario 1
db Port2,1              ; puerto secundario 2
db Port3,1              ; puerto secundario 3

db PortUsbC,1

; inicializar variables
ivar Port1              ; mover ds a la primera variable
pub 1,2,3,4             ; setear variables

; hacer 
ivar Port3              ; setea ds a la variable Port3 en su direccion
align 0                 ; setea el offset a 0
mov a                   ; mueve el valor a -> ds[off] (Port3[0] / *Port3), mov solo con un registro no hace mov, hace brd

in a,b                  ; portea eso