import serial
import serial.tools.list_ports

def get_comports():
    return [cp for cp in serial.tools.list_ports.comports() if cp[2] != "n/a"]

def print_ports():
    comports = get_comports()
    for name, description, hwid in sorted(comports):
        print("{}: {} [{}]".format(name, description, hwid))

def main():
    pass

if __name__ == '__main__':
    main()