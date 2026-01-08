db ConditionsComparte,2
ivar ConditionsComparte,0
align 0
pub 1,1

call start

label is_equal
    pub 'c',7,'q',7
    ret

label is_not_equal
    pub 'c',7,'n',7,'q',7
    ret

label is_greater
    pub 'c',7,'g',7
    ret

label is_not_greater
    pub 'c',7,'n',7,'g',7
    ret

label start

    ivar ConditionsComparte,0
    align 0
    gub a
    gub b

    cmp a,b

    ivar 0xB82,0
    align 0

    cq is_equal
    cnq is_not_equal
    cg is_greater
    cng is_not_greater