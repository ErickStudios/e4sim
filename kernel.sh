python e4asm.py examples/bsex.asm examples/bsex.o
python e4usbtool.py -new examples/test.img examples/bsex.o
python e4usbtool.py -cpy examples/test.img examples/test.txt /test.txt

# ejecutar el e4sim.py
python e4sim.py                             \
    -onlydisplay                            \
    -autopower                              \
    -usb examples/test.img