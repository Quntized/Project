import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

print("\n=== AVAILABLE PORTS ===")
found_any = False
for p in ports:
    found_any = True
    print(f"Device: {p.device}")
    print(f"Name:   {p.name}")
    print(f"Desc:   {p.description}")
    print(f"HWID:   {p.hwid}")
    print("-----------------------")

if not found_any:
    print("No serial ports found! Check your USB cable.")
print("=======================\n")
