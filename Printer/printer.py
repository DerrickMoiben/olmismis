# from escpos.printer import Usb

# printer = Usb(0x0fe6, 0x811e, in_ep=0x82, out_ep=0x01)

# printer.set(align='center', font='b', text_type='normal', width=2, height=2)
# printer.cut()

import json


with open('apis/messages.json') as f:
    data = json.load(f)
    print(data[0:-1])