import time
import board
import usb_cdc  # pyright: ignore[reportMissingImports]
import analogio  # pyright: ignore[reportMissingImports]

from eng_utils import logger

logger.info("Initializing Resistor Test")

HEARTBEAT_FREQUENCY_SEC = 2
POLLING_INTERVAL_SEC = 0.01

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

value_resolution = 10

class Main:
    def __init__(self):
        logger.info(f"Initializing Main")

    def get_voltage(self):
        return (self.input_pin.value // value_resolution * value_resolution * 3.3) / 65536

    def mainLoop(self):
        self.input_pin = analogio.AnalogIn(board.A0)

        logger.info(f"Monitoring analog input on A0")
        logger.info(f"Reference voltage {self.input_pin.reference_voltage}V")

        nextHeartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC
        nextAnalogPoll = time.monotonic() + POLLING_INTERVAL_SEC

        max_delta_threshold = 0.02
        delta_exception_reset_threshold = 0.04
        delta_exceptions = 0
        last_delta_exception_reset_sec = time.monotonic()
        
        last_voltage = self.get_voltage()
        last_deltav = 0

        # calculate the trailing average of the input value to smooth out noise
        trailing_average_sample_size = 20
        trailing_average_index = 0
        trailing_voltage = [last_voltage] * trailing_average_sample_size
        trailing_deltav = [last_deltav] * trailing_average_sample_size
        max_voltage = 0.0
        min_voltage = 999.0
        max_deltav = 0.0
        min_deltav = 999.0
        total_deltav = 0.0
        avg_deltav_samples = 0

        while True:
            if time.monotonic() > nextAnalogPoll:
                nextAnalogPoll = time.monotonic() + POLLING_INTERVAL_SEC

                input_voltage = self.get_voltage()
                trailing_voltage[trailing_average_index] = input_voltage

                deltav = abs(input_voltage - last_voltage)

                trailing_deltav[trailing_average_index] = deltav

                last_voltage = input_voltage
                last_deltav = deltav

                trailing_average_index += 1

                if(trailing_average_index >= trailing_average_sample_size):
                    trailing_average_index = 0
                    smoothed_voltage = sum(trailing_voltage) / len(trailing_voltage)
                    max_voltage = max(max_voltage, smoothed_voltage)
                    min_voltage = min(min_voltage, smoothed_voltage)

                    smoothed_deltav = sum(trailing_deltav) / len(trailing_deltav)
                    max_deltav = max(max_deltav, deltav)
                    total_deltav += deltav
                    avg_deltav_samples += 1
                    avg_deltav = total_deltav / avg_deltav_samples

                    logString = f"V: {smoothed_voltage:4.2f}/∧{max_voltage:4.2f}/∨{min_voltage:<4.2f} "
                    logString += f" - ΔV: {smoothed_deltav:6.4f} / μΔV {avg_deltav:<6.4f} / ∧ΔV {max_deltav:6.4f} "
                    logString += f" - Excp {delta_exceptions} - reset: {time.monotonic() - last_delta_exception_reset_sec:.2f}s ago"
                    
                    if smoothed_deltav > max_delta_threshold:
                        logString += " ***************"
                        delta_exceptions += 1

                        if smoothed_deltav >= delta_exception_reset_threshold:
                            max_voltage = 0.0
                            min_voltage = 999.0
                            max_deltav = 0.0
                            min_deltav = 999.0
                            total_deltav = 0.0
                            avg_deltav_samples = 0
                            delta_exceptions = 0
                            last_delta_exception_reset_sec = time.monotonic()

                    logger.info(logString)

            if time.monotonic() > nextHeartbeat:
                # logString = "** Heartbeat"
                # logger.info(logString)
                nextHeartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC


main = Main()
main.mainLoop()