; struct Example {
;   u8 c8;
;   u16 c16;
;   u32 c32;
;   u64 c64;
; }
;; e4c: struct created Example with size 13

; struct Example MyStruct;
db MyStruct,13 ;; e4c: create struct

; MyStruct.c8 = 8;
ivar MyStruct,0 ;; e4c: struct solve
align 0 ;; e4c: reset offset
mov [byte]8 ;; e4c: set var

; MyStruct.c16 = 16;
ivar MyStruct,0 ;; e4c: struct solve
align 0 ;; e4c: reset offset
gub a ;; e4c: skip c8
mov [byte]16 ;; e4c: set var

; MyStruct.c32 = 32;
ivar MyStruct,0 ;; e4c: struct solve
align 0 ;; e4c: reset offset
gub a ;; e4c: skip c8
gul a ;; e4c: skip c16
mov [byte]32 ;; e4c: set offset

; MyStruct.c64 = 64;
ivar MyStruct,0 ;; e4c: struct solve
align 0 ;; e4c: reset offset
gub a ;; e4c: skip c8
gul a ;; e4c: skip c16
gul a ;; e4c: skip c32
mov [byte]64 ;; e4c: set offset
