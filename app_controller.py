# coding: UTF-8

from PySide2.QtWidgets import QDialog, QApplication, QMessageBox, QComboBox, QPushButton, QHBoxLayout
from PySide2.QtCore import QTimer, Qt
from PySide2.QtGui import QColor, QFont, QScreen, QStandardItemModel, QStandardItem
import sys
import os
import time
from datetime import datetime

# Import auto-generated UI
from ui_UI_Resistance import Ui_Dialog

# Import custom modules
from measurement_worker import MeasurementWorker
from port_scanner import scan_ports, get_all_ports, verify_hioki_connection
from insert_resistance2db import insert_to_mssql


class HiokiResistanceApp(QDialog):
    """
    Main application controller for HIOKI Resistance Meter UI.
    Manages device connection, measurements, UI updates, and database logging.
    """

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("HIOKI Resistance Meter")

        # Application state
        self.connected = False
        self.measurement_worker = None
        self.current_port = None
        self.current_model = None
        self.measurement_count = 0

        # Auto-reconnect state
        self.auto_reconnect_enabled = False
        self.reconnect_timer = QTimer()
        self.reconnect_timer.timeout.connect(self._on_reconnect_timer)

        # Setup logger model for QListView using QStandardItemModel
        self.log_model = QStandardItemModel()
        self.ui.listView_logger.setModel(self.log_model)

        # Add port selection and connect button programmatically to status group
        self._add_port_controls()

        # Initialize UI
        self._setup_ui()
        self._apply_responsive_scaling()
        self._populate_ports()

    def _add_port_controls(self):
        """Add port dropdown and connect button to status group."""
        # Create port combo box
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(150)
        self.port_combo.currentTextChanged.connect(self._on_port_selected)

        # Create connect button
        self.connect_button = QPushButton("Connect")
        self.connect_button.setMaximumWidth(100)
        self.connect_button.clicked.connect(self._connect_device)

        # Add to status group layout
        layout = self.ui.groupBox_status.layout()
        layout.addWidget(self.port_combo)
        layout.addWidget(self.connect_button)

    def _setup_ui(self):
        """Setup UI signal/slot connections."""
        # Model button - show device info (correct name from UI file)
        self.ui.pushButton_model.clicked.connect(self._on_model_button_clicked)

        # Measurement spinboxes - read-only
        self.ui.doubleSpinBox_UpperLimit.setReadOnly(True)
        self.ui.doubleSpinBox_lowerLimit.setReadOnly(True)
        self.ui.doubleSpinBox_Measure.setReadOnly(True)

        # Pass/Fail button - status display only
        self.ui.pushButton_Judgement.setEnabled(False)
        self._update_pass_fail_button("UNKNOWN")

        # Initial status - use existing label
        self._update_status_label("Disconnected", "Not connected")

        # Setup logger (no signal handler needed for simple display)
        # Removed itemSelectionChanged as it's not needed

    def _apply_responsive_scaling(self):
        """
        Apply responsive scaling based on screen size.
        Scales fonts, buttons, and spinbox sizes for small screens.
        """
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.geometry()
            height = geometry.height()
            width = geometry.width()

            # Calculate scale factor
            if height < 800:
                scale_factor = height / 800.0
            else:
                scale_factor = 1.0

            if scale_factor < 1.0:
                # Small screen - reduce font sizes and widget dimensions
                self._scale_ui_elements(scale_factor)

    def _scale_ui_elements(self, scale_factor):
        """
        Scale UI elements (fonts, button sizes, spinboxes) by scale factor.
        
        Args:
            scale_factor (float): Scale multiplier (e.g., 0.6 for 60% of original)
        """
        # Scale resistance measurement spinbox font
        font = self.ui.doubleSpinBox_Measure.font()
        original_size = font.pointSize()
        if original_size > 0:
            font.setPointSize(int(original_size * scale_factor))
            self.ui.doubleSpinBox_Measure.setFont(font)

        # Scale pass/fail button font
        btn_font = self.ui.pushButton_Judgement.font()
        if btn_font.pointSize() > 0:
            btn_font.setPointSize(int(btn_font.pointSize() * scale_factor))
            self.ui.pushButton_Judgement.setFont(btn_font)

        # Scale spinbox fonts (limits)
        for spinbox in [self.ui.doubleSpinBox_UpperLimit, self.ui.doubleSpinBox_lowerLimit]:
            sb_font = spinbox.font()
            if sb_font.pointSize() > 0:
                sb_font.setPointSize(int(sb_font.pointSize() * scale_factor))
                spinbox.setFont(sb_font)

        # Scale log list font
        log_font = self.ui.listView_logger.font()
        if log_font.pointSize() > 0:
            log_font.setPointSize(max(8, int(log_font.pointSize() * scale_factor)))
            self.ui.listView_logger.setFont(log_font)

        # Adjust window geometry if needed
        if scale_factor < 0.75:
            self.resize(int(1280 * scale_factor), int(800 * scale_factor))

    def _populate_ports(self):
        """
        Populate COM port dropdown and auto-scan for HIOKI device.
        """
        self.port_combo.clear()

        ports = get_all_ports()
        if not ports:
            self.port_combo.addItem("No ports available")
            self._update_status_label("Port Error", "No COM ports found")
            return

        # Add all ports
        for port in ports:
            self.port_combo.addItem(port)

        # Auto-scan for HIOKI device
        self._auto_scan_device()

    def _auto_scan_device(self):
        """
        Auto-scan for HIOKI device and pre-select it in the dropdown.
        """
        from port_scanner import scan_ports
        
        self._log_message("[INFO] Scanning for HIOKI device...")
        port, model = scan_ports()

        if port:
            self._update_status_label("Device Found", f"HIOKI {model}")
            self.port_combo.setCurrentText(port)
            self.current_port = port
            self.current_model = model
            self._log_message(f"[FOUND] HIOKI device: {model} on port {port}")
            # Auto-connect
            self._connect_device()
        else:
            self._update_status_label("Scanning", "No HIOKI device found")
            self._log_message("[WARN] No HIOKI device detected. Manual port selection available.")

    def _on_port_selected(self, port_name):
        """Handle port selection from dropdown."""
        if port_name and port_name != "No ports available":
            self.current_port = port_name

    def _on_model_button_clicked(self):
        """Handle Model button click - show device info."""
        if self.connected and self.current_model:
            QMessageBox.information(
                self,
                "Device Information",
                f"Connected Device:\n\nModel: {self.current_model}\nPort: {self.current_port}\nBaud Rate: 9600"
            )
        else:
            QMessageBox.warning(self, "Not Connected", "Device is not connected.")

    def connect_device(self):
        """Public method to connect to device (called from external button if needed)."""
        self._connect_device()

    def _connect_device(self):
        """Internal method to connect to device and start measurements."""
        if not self.current_port:
            QMessageBox.warning(self, "No Port", "Please select a COM port first.")
            return

        self._log_message(f"[CONNECT] Attempting connection to {self.current_port}...")
        self._update_status_label("Connecting", f"Port: {self.current_port}")

        # Verify HIOKI device
        success, result = verify_hioki_connection(self.current_port, 9600, timeout=2.0)
        if success:
            self.current_model = result
            self._log_message(f"[SUCCESS] Connected to {self.current_model}")
            self._update_status_label("Connected", f"HIOKI {self.current_model}")

            # Query device limits
            self._query_device_limits()

            # Start measurement worker
            self._start_measurement_worker()
            self.connected = True
            self.auto_reconnect_enabled = True
        else:
            self._log_message(f"[ERROR] Connection failed: {result}")
            self._update_status_label("Connection Failed", result)
            QMessageBox.critical(self, "Connection Error", f"Failed to connect:\n{result}")

    def _query_device_limits(self):
        """Query upper and lower limits from device."""
        from usb_rs import Usb_rs
        
        try:
            ser = Usb_rs(gui=False)
            if ser.open(self.current_port, 9600):
                upper = ser.SendQueryMsg("JUDGE:LEVEL:UPPER?", timeout=2.0)
                lower = ser.SendQueryMsg("JUDGE:LEVEL:LOWER?", timeout=2.0)
                ser.close()

                if upper != "Error" and lower != "Error":
                    try:
                        upper_val = float(upper)
                        lower_val = float(lower)
                        self.ui.doubleSpinBox_UpperLimit.setValue(upper_val)
                        self.ui.doubleSpinBox_lowerLimit.setValue(lower_val)
                        self._log_message(f"[LIMITS] Upper: {upper_val:.3f}Ω | Lower: {lower_val:.3f}Ω")
                    except ValueError:
                        pass
        except Exception as e:
            self._log_message(f"[WARN] Could not query limits: {str(e)}")

    def _start_measurement_worker(self):
        """Start the background measurement worker thread."""
        if self.measurement_worker is not None:
            self.measurement_worker.stop()

        self.measurement_worker = MeasurementWorker()
        self.measurement_worker.set_connection_params(self.current_port, 9600)

        # Connect worker signals to slots
        self.measurement_worker.measurement_signal.connect(self._on_measurement_received)
        self.measurement_worker.error_signal.connect(self._on_measurement_error)
        self.measurement_worker.connection_lost_signal.connect(self._on_connection_lost)
        self.measurement_worker.reconnect_status_signal.connect(self._on_reconnect_status)
        self.measurement_worker.limits_signal.connect(self._on_limits_received)

        self.measurement_worker.start()
        self._log_message("[WORKER] Measurement started (500ms interval)")

    def _on_measurement_received(self, value, timestamp, pass_fail_status):
        """
        Handle measurement signal from worker thread.
        
        Args:
            value (float): Resistance value in ohms
            timestamp (str): Measurement timestamp (HH:MM:SS)
            pass_fail_status (str): "PASS" or "FAIL"
        """
        # Update UI
        self.ui.doubleSpinBox_Measure.setValue(value)
        self._update_pass_fail_button(pass_fail_status)

        # Log to UI
        status_color = "✓" if pass_fail_status == "PASS" else "✗"
        self._log_message(f"[{timestamp}] {value:.4f}Ω | {pass_fail_status} {status_color}")

        # Insert to database
        self._insert_to_database(value, pass_fail_status)

        self.measurement_count += 1

    def _on_measurement_error(self, error_msg):
        """Handle measurement error signal."""
        self._log_message(f"[ERROR] {error_msg}")

    def _on_connection_lost(self, lost):
        """Handle connection lost signal."""
        if lost:
            self._log_message("[ALERT] Connection lost! Attempting auto-reconnect...")
            self.connected = False
            self.auto_reconnect_enabled = True
            self.reconnect_timer.start(1000)  # Check every 1 second

    def _on_reconnect_status(self, status_msg):
        """Handle reconnect status updates."""
        self._update_status_label("Reconnecting", status_msg)
        self._log_message(f"[RECONNECT] {status_msg}")

    def _on_limits_received(self, upper, lower):
        """Handle limits signal from worker."""
        self.ui.doubleSpinBox_UpperLimit.setValue(upper)
        self.ui.doubleSpinBox_lowerLimit.setValue(lower)

    def _on_reconnect_timer(self):
        """Timer callback to attempt reconnection."""
        if not self.connected and self.auto_reconnect_enabled:
            # Worker thread will handle reconnection automatically
            # This timer is just to ensure we keep trying
            pass

    def _update_pass_fail_button(self, status):
        """
        Update Pass/Fail button appearance based on status.
        
        Args:
            status (str): "PASS", "FAIL", or "UNKNOWN"
        """
        if status == "PASS":
            self.ui.pushButton_Judgement.setStyleSheet(
                "background-color: #00AA00; color: white; font-weight: bold; border: 2px solid #008800;"
            )
            self.ui.pushButton_Judgement.setText("PASS")
        elif status == "FAIL":
            self.ui.pushButton_Judgement.setStyleSheet(
                "background-color: #FF0000; color: white; font-weight: bold; border: 2px solid #AA0000;"
            )
            self.ui.pushButton_Judgement.setText("FAIL")
        else:
            self.ui.pushButton_Judgement.setStyleSheet(
                "background-color: #888888; color: white; font-weight: bold; border: 2px solid #666666;"
            )
            self.ui.pushButton_Judgement.setText("UNKNOWN")

    def _update_status_label(self, status_title, status_detail):
        """
        Update status label in UI.
        
        Args:
            status_title (str): Main status (e.g., "Connected", "Disconnected")
            status_detail (str): Detail message
        """
        status_text = f"{status_title}\n{status_detail}"
        self.ui.label_ConnectionStatus.setText(status_text)

    def _log_message(self, message):
        """
        Log message to UI list.
        
        Args:
            message (str): Message to log
        """
        # Add to model as QStandardItem
        item = QStandardItem(message)
        self.log_model.appendRow(item)
        
        # Auto-scroll to latest
        last_index = self.log_model.index(self.log_model.rowCount() - 1)
        self.ui.listView_logger.scrollTo(last_index)

    def _insert_to_database(self, value, status):
        """
        Insert measurement to database asynchronously.
        
        Args:
            value (float): Resistance value
            status (str): "PASS" or "FAIL"
        """
        if not self.current_model:
            return

        try:
            # This will run in the GUI thread, but since DB insert is relatively fast
            # we could make it async if needed
            insert_to_mssql(self.current_model, value, status)
        except Exception as e:
            # Log error but don't stop measurements
            self._log_message(f"[DB] Database error: {str(e)}")

    def closeEvent(self, event):
        """Handle application close."""
        if self.measurement_worker is not None:
            self.measurement_worker.stop()
        self.reconnect_timer.stop()
        event.accept()
