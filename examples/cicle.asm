
db data,4

align 0
ivar data,0
pub 12
align 0
gub cycl

call lp

; loop
label lp
    dbg cycl
    loop lp

; hang
label hang
    cli
    hlt