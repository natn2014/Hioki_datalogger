# coding: UTF-8

from PySide2.QtCore import QThread, Signal, QTimer
import time
from usb_rs import Usb_rs


class MeasurementWorker(QThread):
    """
    Background worker thread for continuous HIOKI device measurements.
    Runs measurement loop every 500ms and emits signals for UI updates.
    """

    # Signals
    measurement_signal = Signal(float, str, str)  # (value, timestamp, pass_fail_status)
    error_signal = Signal(str)                     # error_message
    connection_lost_signal = Signal(bool)          # True when connection lost
    reconnect_status_signal = Signal(str)          # "Reconnecting...", "Connected", etc.
    limits_signal = Signal(float, float)           # (upper_limit, lower_limit)

    def __init__(self):
        super().__init__()
        self.ser = Usb_rs(gui=False)
        self.running = False
        self.port = None
        self.speed = 9600
        self.measurement_interval = 0.5  # 500ms in seconds
        self.timeout = 3.0  # 3 second timeout for device response
        self.retry_attempts = 0
        self.max_retries = 10
        self.retry_interval = 5  # 5 seconds between retries
        self.last_error_time = 0
        self.measurement_count = 0

    def set_connection_params(self, port, speed=9600):
        """Set serial port and baud rate before starting."""
        self.port = port
        self.speed = speed

    def run(self):
        """Main measurement loop (runs in separate thread)."""
        self.running = True
        self.retry_attempts = 0
        last_measurement_time = time.time()
        last_reconnect_attempt = time.time()

        while self.running:
            current_time = time.time()

            # Try to connect if not already connected
            if not self.ser.ser or not self.ser.ser.is_open:
                if current_time - last_reconnect_attempt >= self.retry_interval:
                    self._attempt_reconnect()
                    last_reconnect_attempt = current_time
                time.sleep(0.1)
                continue

            # Measurement loop at 500ms interval
            if current_time - last_measurement_time >= self.measurement_interval:
                success = self._perform_measurement()
                if not success:
                    # Connection likely lost
                    self.connection_lost_signal.emit(True)
                    self.ser.close()
                last_measurement_time = current_time

            time.sleep(0.05)  # Small sleep to prevent busy-waiting

        # Cleanup
        if self.ser.ser and self.ser.ser.is_open:
            self.ser.close()

    def _attempt_reconnect(self):
        """Attempt to reconnect to the device."""
        if self.retry_attempts >= self.max_retries:
            self.reconnect_status_signal.emit(
                f"Reconnection failed after {self.max_retries} attempts. Manual retry needed."
            )
            return

        self.reconnect_status_signal.emit(
            f"Reconnecting... (Attempt {self.retry_attempts + 1}/{self.max_retries})"
        )

        try:
            # Close existing connection
            if self.ser.ser and self.ser.ser.is_open:
                self.ser.close()

            # Attempt to open port
            if self.ser.open(self.port, self.speed):
                # Verify connection with *IDN? query
                response = self.ser.SendQueryMsg("*IDN?", self.timeout)
                if response != "Error" and response != "Timeout Error":
                    self.retry_attempts = 0
                    self.reconnect_status_signal.emit("Connected")
                    self.connection_lost_signal.emit(False)
                    # Query limits on successful reconnect
                    self._query_limits()
                    return
                else:
                    self.ser.close()
                    self.retry_attempts += 1
            else:
                self.retry_attempts += 1
        except Exception as e:
            self.error_signal.emit(f"Reconnection error: {str(e)}")
            self.retry_attempts += 1

    def _perform_measurement(self):
        """Perform a single measurement cycle."""
        try:
            # Query resistance value
            resistance_str = self.ser.SendQueryMsg("MEAS:RES?", self.timeout)

            if resistance_str == "Error" or resistance_str == "Timeout Error":
                self.error_signal.emit(f"Measurement error: {resistance_str}")
                return False

            # Parse resistance value
            try:
                resistance_value = float(resistance_str)
            except ValueError:
                self.error_signal.emit(f"Invalid resistance value: {resistance_str}")
                return False

            # Query pass/fail status
            judge_result_str = self.ser.SendQueryMsg("JUDGE:RESULT?", self.timeout)
            if judge_result_str == "Error" or judge_result_str == "Timeout Error":
                pass_fail_status = "UNKNOWN"
            else:
                try:
                    judge_result = int(float(judge_result_str))
                    pass_fail_status = "PASS" if judge_result == 0 else "FAIL"
                except ValueError:
                    pass_fail_status = "UNKNOWN"

            # Generate timestamp
            timestamp = time.strftime("%H:%M:%S")

            # Emit measurement signal
            self.measurement_signal.emit(resistance_value, timestamp, pass_fail_status)
            self.measurement_count += 1

            return True

        except Exception as e:
            self.error_signal.emit(f"Measurement exception: {str(e)}")
            return False

    def _query_limits(self):
        """Query upper and lower limits from device."""
        try:
            upper_str = self.ser.SendQueryMsg("JUDGE:LEVEL:UPPER?", self.timeout)
            lower_str = self.ser.SendQueryMsg("JUDGE:LEVEL:LOWER?", self.timeout)

            if upper_str != "Error" and lower_str != "Error":
                try:
                    upper_limit = float(upper_str)
                    lower_limit = float(lower_str)
                    self.limits_signal.emit(upper_limit, lower_limit)
                except ValueError:
                    pass  # Silently skip if limits can't be parsed
        except Exception:
            pass  # Silently skip limit query failures

    def stop(self):
        """Stop the measurement loop and close connection."""
        self.running = False
        self.wait()  # Wait for thread to finish

    def manual_reconnect(self):
        """Reset retry counter and force immediate reconnection attempt."""
        self.retry_attempts = 0
