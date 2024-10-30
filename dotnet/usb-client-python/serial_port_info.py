import serial.tools.list_ports

from utils import log_debug


class SerialPortInfo:
    @classmethod
    def scan_serial_ports(cls) -> list["SerialPortInfo"]:
        retval = []

        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            port_info = SerialPortInfo(p)
            retval.append(port_info)
            log_debug(f"Found serial port: {port_info}")

        return retval

    def __init__(self, port):
        self.name = port.name
        self.pid = port.pid
        self.vid = port.vid
        self.serial_number = port.serial_number

    def __str__(self):
        return f"{self.name}: VID: {self.vid}, PID: {self.pid}, SerialNumber: {self.serial_number}"
