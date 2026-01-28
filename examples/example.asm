; ejemplo en assembly

; Erick4004 ISA
; registros: a=0x1, b=0x2, c=0x3, d=0x4, e=0x5, f=0x6, ds=0x7
; 01 XY <- X=Reg1, Y=Reg2
; 02 AA BB BB BB BB (int8 A=size), (uint32_t B=Direction)

ivar 0xB82,4                ; settear ds a la direccion
align 0                     ; settear off a 0

pub 'h',0xf,'e',0xf,'l',0xf,'l',0xf,'o',0xf         ; hello
pub 32,0xf,'w',0xf,'o',0xf,'r',0xf,'l',0xf,'d',0xf  ; world

pub 0
