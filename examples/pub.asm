; como es setear un registro por ejemplo a
ivar 0x80,0                     ; ds -> 0x80, 0x80 es una direccion de ejemplo donde usaremos los valores
align 0                         ; offset -> 0
pub 5                           ; el valor que queremos añadir
align 0                         ; offset -> 0
gub a                           ; obtener el valor en el registro a