import serial
import time
import sys
import struct


def setup_injection(_serial):
    print("==============================")
    print("Injecting...")
    while True:
        _serial.write('ssssss')
        output = _serial.read(40)
        if 'autoboot' in output:
            break
    _serial.write('\n')
    _serial.read(1024)
    print("Inject success.")


def write_mw(_serial, addr, val):
    command = "mw {0:08x} {1:08x}\n".format(addr, val)
    num = _serial.write(command)
    if num != 21:
        print("write_mw write length mismatch:" + str(num))
        return False

    echo_output = _serial.read(31)
    if command.strip() not in echo_output.strip():
        print("write_mw echo mismatch:" + str(command))
        return False

    return True


def load_file_to_memory(_serial, addr_hex, file_path, addr_hex_offset="00000000"):
    print("==============================")
    print("Loading file to memory....")

    payload = open(file_path, "rb").read()
    payload_size = len(payload)

    index_addr_dec = int(addr_hex, 16)
    last_time = time.time()
    for i in range(0, payload_size, 4):
        if i % 5000 == 0 and i != 0:
            time_delta = time.time() - last_time
            last_time = time.time()
            eta_minutes_left = ((time_delta / 5000.0) * (payload_size - i + 1)) / 60.0
            print("ETA Left: %2.2fm" % eta_minutes_left)

        if int(addr_hex_offset, 16) <= index_addr_dec:
            int_value = struct.unpack('<I', payload[i:i+4])[0]
            if not write_mw(_serial, index_addr_dec, int_value):
                if not write_mw(_serial, index_addr_dec, int_value):
                    print("command retry failed..")
                    sys.exit(-1)

        index_addr_dec += 4
    print("Memory load success: %s loaded to addr:0x%s" % (file_path,addr_hex))


def boot_system(_serial, addr_hex):
    print("==============================")
    print("Booting....")
    _serial.write(b'setenv bootargs console=${console} root=${nand_root} init=${init} loglevel=${loglevel} partitions=${partitions} mem=255M\n')
    line = _serial.read(150)
    sys.stdout.write(line)

    _serial.write(b"boota %s\n" % addr_hex)
    for i in range(0, 10000):
        line = _serial.read(150)
        if line is not None and len(line) > 0:
            sys.stdout.write(line)
    print("Booting Success.")


def main():
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.4)

    setup_injection(ser)
    load_file_to_memory(ser, '40007800', 'kernel.bin')
    boot_system(ser, '40007800')


if __name__ == "__main__":
    main()
