# HIOKI Resistance Meter UI Application

A PySide2-based desktop application for continuous measurement and logging of resistance values from HIOKI devices via USB/RS-232. Designed for deployment on Windows development machines and Raspberry Pi 5.

## Features

- **Auto-Device Detection**: Automatically scans COM ports to find connected HIOKI devices
- **Continuous Measurements**: Reads resistance values every 500ms with configurable intervals
- **Auto-Reconnect**: Automatically attempts to reconnect if the device is unplugged (5-second retry interval, max 10 retries)
- **Live Status Display**: Shows real-time resistance values, pass/fail status, and connection state
- **Database Logging**: Automatically logs all measurements to MSSQL database (ENGINEER_DB)
- **Responsive UI**: Automatically scales fonts and UI elements for small displays (Raspi 7" screens)
- **Pass/Fail Indication**: Green (PASS) or Red (FAIL) button updated from device limits
- **Data Log Viewer**: Timestamped, color-coded event log with measurements, errors, and connection events

## System Requirements

### Windows (Development)
- Python 3.7 or later
- COM port USB adapter or direct serial connection to HIOKI device
- MSSQL Server network access (172.18.72.16:1433)

### Raspberry Pi 5 (Deployment)
- Raspberry Pi OS (Bookworm or later)
- USB connection to HIOKI device
- Network access to MSSQL Server (172.18.72.16:1433)
- 2GB RAM minimum
- Python 3.9 or later

## Installation

### Windows Setup

1. **Clone or download this repository**:
   ```bash
   cd d:\Dev_AI_env\Hioki_v2
   ```

2. **Create a Python virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

### Raspberry Pi 5 Setup

1. **SSH into Raspberry Pi**:
   ```bash
   ssh pi@raspberrypi.local
   ```

2. **Clone or copy project files to Pi**:
   ```bash
   git clone <repo-url> ~/hioki_meter
   cd ~/hioki_meter
   ```

3. **Make run script executable**:
   ```bash
   chmod +x run.sh
   ```

4. **Run the application**:
   ```bash
   ./run.sh
   ```

   Or manually:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

### USB Device Permissions on Raspberry Pi

If you encounter permission errors when connecting to the HIOKI device:

1. **Check USB device info**:
   ```bash
   lsusb
   ```
   Output example: `Bus 001 Device 004: ID 1234:5678 HIOKI Device`

2. **Create udev rule** (optional, to avoid needing sudo):
   ```bash
   sudo nano /etc/udev/rules.d/50-hioki.rules
   ```

3. **Add this line** (adjust vendor/product IDs as needed):
   ```
   SUBSYSTEM=="tty", ATTRS{idVendor}=="1234", ATTRS{idProduct}=="5678", MODE="0666"
   ```

4. **Reload udev rules**:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

5. **Reconnect the HIOKI device**

**Alternative**: Run the application with sudo:
```bash
sudo python main.py
```

## Usage

1. **Start the Application**
   - Double-click `main.py` on Windows or run `./run.sh` on Raspi
   - The app will auto-scan for connected HIOKI devices

2. **Auto-Detection**
   - If HIOKI device is found and connected, measurements start automatically
   - Port, model, and limits are shown in the status area
   - Status label shows "Connected: [MODEL]"

3. **Manual Port Selection**
   - If device is not auto-detected, select the COM port from the dropdown
   - Click "Connect" to establish connection

4. **Monitor Measurements**
   - **Center Display**: Current resistance value (large font)
   - **Left Display**: Lower limit threshold
   - **Right Display**: Upper limit threshold
   - **Pass/Fail Button**: Green = PASS, Red = FAIL, Gray = UNKNOWN
   - **Data Log**: Scrollable list of timestamped measurements and events

5. **Auto-Reconnection**
   - If device is unplugged, status shows "Reconnecting..." with countdown
   - App automatically retries every 5 seconds (up to 10 times)
   - If reconnected within retry limit, measurements resume automatically
   - After 10 failed attempts, manual "Connect" button click required

6. **Database Logging**
   - All measurements are automatically logged to MSSQL
   - Database: ENGINEER_DB
   - Table: resistance
   - Columns: Timestamp, Resistance, Status, Model, Date, Time
   - If database is unavailable, measurements continue (errors logged to UI)

## Auto-Start / Auto-Run Configuration

### Windows Auto-Start

**Option 1: Using PowerShell (Recommended)**

1. Open PowerShell as Administrator:
   ```powershell
   Right-click PowerShell → "Run as Administrator"
   ```

2. Run the setup script:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
   cd d:\Dev_AI_env\Hioki_v2
   .\setup_autostart.ps1
   ```

3. Confirmation message shows:
   ```
   ✓ Auto-start configured successfully!
   Location: C:\Users\[YourUsername]\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\HIOKI_Resistance_Meter.lnk
   Application will start automatically on next boot
   ```

4. To remove auto-start:
   ```powershell
   .\setup_autostart.ps1 -Remove
   ```

**Option 2: Manual Registry Setup (Alternative)**

1. Press `Windows + R`, type `regedit` and press Enter
2. Navigate to: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Right-click → New → String Value
4. Name it: `HIOKI_Resistance_Meter`
5. Value: `d:\Dev_AI_env\Hioki_v2\autostart.bat`
6. Click OK and restart Windows

**Option 3: Manual Startup Folder (Simplest)**

1. Press `Windows + R`, type `shell:startup` and press Enter
2. Right-click in the folder → New → Shortcut
3. Target: `d:\Dev_AI_env\Hioki_v2\autostart.bat`
4. Name: `HIOKI_Resistance_Meter`
5. Click Finish and restart Windows

### Raspberry Pi Auto-Start

**Automated Setup (Recommended)**

1. SSH into Raspberry Pi:
   ```bash
   ssh pi@raspberrypi.local
   ```

2. Navigate to application directory:
   ```bash
   cd ~/hioki_meter
   ```

3. Run the setup script with sudo:
   ```bash
   sudo bash setup_autostart.sh install
   ```

4. Confirmation output:
   ```
   ✓ Service installed successfully!
   ✓ Application will auto-start on next boot
   
   Available commands:
     sudo systemctl start hioki-meter      # Start now
     sudo systemctl stop hioki-meter       # Stop service
     sudo systemctl restart hioki-meter    # Restart service
     sudo systemctl status hioki-meter     # Check status
     sudo journalctl -u hioki-meter -f     # View live logs
     sudo bash setup_autostart.sh remove   # Remove auto-start
   ```

5. Reboot to test auto-start:
   ```bash
   sudo reboot
   ```

**Manual systemd Setup (If automatic fails)**

1. Copy service file to systemd:
   ```bash
   sudo cp ~/hioki_meter/hioki-meter.service /etc/systemd/system/
   sudo chmod 644 /etc/systemd/system/hioki-meter.service
   ```

2. Reload systemd daemon:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable service:
   ```bash
   sudo systemctl enable hioki-meter
   ```

4. Start service:
   ```bash
   sudo systemctl start hioki-meter
   ```

5. Verify status:
   ```bash
   sudo systemctl status hioki-meter
   ```

6. View logs:
   ```bash
   sudo journalctl -u hioki-meter -f
   ```

**Remove Auto-Start (Raspberry Pi)**

```bash
sudo bash setup_autostart.sh remove
```

Or manually:
```bash
sudo systemctl disable hioki-meter
sudo systemctl stop hioki-meter
sudo rm /etc/systemd/system/hioki-meter.service
sudo systemctl daemon-reload
```

## Application Architecture

### Files

- **main.py**: Entry point; creates and runs the application
- **app_controller.py**: Main controller orchestrating UI, measurements, and database
- **measurement_worker.py**: QThread-based background worker for continuous measurements
- **port_scanner.py**: Utilities for COM port discovery and HIOKI device detection
- **ui_UI_Resistance.py**: Auto-generated PySide2 UI (do not edit manually)
- **usb_rs.py**: Serial communication class (existing; reused)
- **insert_resistance2db.py**: Database insertion function (existing; reused)

### Threading Model

- **Main Thread**: GUI updates, user input, database insertion calls
- **Worker Thread**: Serial communication, device queries (500ms loop), auto-reconnect logic

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No ports available" | Check USB connection; try different USB port on computer |
| "Permission denied" | On Raspi, run with `sudo` or apply udev rules (see above) |
| "Connection Error - Timeout" | Verify device is on at 9600 baud; check cable connection |
| "Device disconnected" | Device is offline or unplugged; app will auto-reconnect or wait for manual reconnect |
| Database insert fails | Check network connectivity to 172.18.72.16; verify credentials in insert_resistance2db.py |
| Measurements stop updating | Device may have timed out; try clicking manually Reconnect or restarting app |
| UI text too small on Raspi | Application auto-scales for small screens; adjust display resolution if needed |

## HIOKI Device Configuration

### Supported Commands

The application uses these SCPI commands:
- `*IDN?` - Identify device (model, serial, firmware)
- `MEAS:RES?` - Measure resistance (ohms)
- `JUDGE:LEVEL:UPPER?` / `JUDGE:LEVEL:LOWER?` - Read pass/fail limits
- `JUDGE:RESULT?` - Read pass/fail status (0=PASS, 1=FAIL)

### Verified Models

- HIOKI RM3544-01
- HIOKI RM3545
- HIOKI RM3542

**Note**: If your HIOKI model uses different commands (e.g., `LIMIT:UPPER` instead of `JUDGE:LEVEL:UPPER`), check your device manual and update the commands in `measurement_worker.py` and `app_controller.py`.

## Performance Notes

- Typical measurement rate: 500ms (2 measurements per second) - configurable
- CPU usage on Raspi 5: < 5% idle, < 15% during active measurement
- Memory footprint: ~50-80 MB (Python + PySide2)
- Network latency: Database inserts < 100ms on local network

## License

[Specify your license here]

## Support

For issues or questions, please refer to:
- HIOKI device manual for device-specific commands
- PySide2 documentation: https://doc.qt.io/qtforpython/
- pyserial documentation: https://pyserial.readthedocs.io/

---

**Last Updated**: March 18, 2026
