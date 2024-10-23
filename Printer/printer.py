from escpos.printer import Usb

# Initialize the printer with the correct Vendor ID and Product ID for Epson L3250
printer = Usb(0x04b8, 0x0202)

# Test printing a simple text with formatting
printer.set(align='center', width=2, height=2)  # Removed 'text_type'
printer.text("Test Print\n")
printer.text("Epson L3250\n")
printer.cut()  # Cut the paper
