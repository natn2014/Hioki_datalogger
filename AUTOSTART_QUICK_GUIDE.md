# HIOKI Resistance Meter - Auto-Start Quick Setup Guide

## Windows Auto-Start ⏚ 

### Method 1: PowerShell (Automated - Recommended) ✓

```powershell
# Open PowerShell as Administrator, then:
cd d:\Dev_AI_env\Hioki_v2
.\setup_autostart.ps1
```

**Result**: Shortcut created in Windows Startup folder. App runs automatically on each boot.

**To Remove**:
```powershell
.\setup_autostart.ps1 -Remove
```

---

### Method 2: Windows File Explorer (Simple Manual)

1. Press `Windows + R`
2. Type: `shell:startup` and press Enter
3. Right-click → New → Shortcut
4. Target: `d:\Dev_AI_env\Hioki_v2\autostart.bat`
5. Name: `HIOKI_Resistance_Meter`
6. Restart Windows

---

### Method 3: Windows Registry (Advanced)

1. Press `Windows + R`, type `regedit`
2. Navigate to: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
3. Right-click → New → String Value
4. Name: `HIOKI_Resistance_Meter`
5. Value: `d:\Dev_AI_env\Hioki_v2\autostart.bat`
6. Restart Windows

---

## Raspberry Pi Auto-Start 🍎

### Fastest Method: Automated Setup Script ✓

```bash
ssh pi@raspberrypi.local
cd ~/hioki_meter
sudo bash setup_autostart.sh install
```

**Result**: Service installed and enabled. App runs automatically on each boot.

**Quick Commands**:
```bash
sudo systemctl start hioki-meter       # Start now
sudo systemctl stop hioki-meter        # Stop
sudo systemctl restart hioki-meter     # Restart
sudo systemctl status hioki-meter      # Check status
sudo journalctl -u hioki-meter -f      # View logs
sudo bash setup_autostart.sh remove    # Remove auto-start
```

---

## Files Included

| File | Purpose |
|------|---------|
| `autostart.bat` | Windows batch script to start app with venv |
| `setup_autostart.ps1` | PowerShell automation for Windows registry/shortcuts |
| `hioki-meter.service` | Systemd service file for Raspberry Pi |
| `setup_autostart.sh` | Bash automation for Raspi systemd setup |

---

## Verification

### Windows
- Restart computer
- HIOKI app should appear automatically after desktop loads
- Check Windows Task Manager → check if `python.exe` is running

### Raspberry Pi
```bash
sudo systemctl status hioki-meter
# Should show: "active (running)" in green
```

---

## Troubleshooting

### Windows
| Issue | Solution |
|-------|----------|
| PowerShell execution denied | Run: `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force` |
| Shortcut not in Startup | Verify path in `shell:startup` folder |

### Raspberry Pi
| Issue | Solution |
|-------|----------|
| "Permission denied" | Ensure running with `sudo` |
| Service fails to start | Check logs: `sudo journalctl -u hioki-meter -n 50` |
| Can't SSH | Verify Raspi hostname/IP: `ping raspberrypi.local` |

---

**Last Updated**: March 18, 2026
