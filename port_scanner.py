# coding: UTF-8

import serial
from serial.tools import list_ports
import time
from usb_rs import Usb_rs


def scan_ports():
    """
    Scan all available COM ports and auto-detect HIOKI device.
    
    Returns:
        tuple: (port, model_name) if device found, (None, None) if not found
    """
    available_ports = list_ports.comports()

    if not available_ports:
        return None, None

    for port_info in available_ports:
        port = port_info.device
        
        try:
            # Attempt connection at standard HIOKI baud rate
            test_ser = Usb_rs(gui=False)
            if not test_ser.open(port, 9600):
                continue

            # Query device identification
            response = test_ser.SendQueryMsg("*IDN?", timeout=2.0)
            test_ser.close()

            if response != "Error" and response != "Timeout Error":
                # Parse response: "HIOKI,MODEL,SERIAL,VERSION"
                parts = response.split(",")
                if len(parts) >= 2:
                    model_name = parts[1].strip()
                    return port, model_name

        except Exception:
            continue

    return None, None


def get_all_ports():
    """
    Get list of all available COM ports.
    
    Returns:
        list: List of port names (e.g., ['COM1', 'COM2'] on Windows or ['/dev/ttyUSB0'] on Linux/Raspi)
    """
    available_ports = list_ports.comports()
    return [port_info.device for port_info in available_ports]


def get_port_info(port):
    """
    Get detailed info about a specific port.
    
    Args:
        port (str): Port name (e.g., 'COM6' or '/dev/ttyUSB0')
    
    Returns:
        dict: Information about the port including product, manufacturer, serial number
    """
    available_ports = list_ports.comports()
    for port_info in available_ports:
        if port_info.device == port:
            return {
                'port': port_info.device,
                'product': port_info.product or 'Unknown',
                'manufacturer': port_info.manufacturer or 'Unknown',
                'serial': port_info.serial_number or 'Unknown'
            }
    return None


def verify_hioki_connection(port, speed=9600, timeout=2.0):
    """
    Verify that a specific port has a HIOKI device connected.
    
    Args:
        port (str): Port name
        speed (int): Baud rate (default 9600)
        timeout (float): Timeout for device query
    
    Returns:
        tuple: (True, model_name) if HIOKI device found, (False, error_message) otherwise
    """
    try:
        test_ser = Usb_rs(gui=False)
        if not test_ser.open(port, speed):
            return False, "Failed to open port"

        response = test_ser.SendQueryMsg("*IDN?", timeout=timeout)
        test_ser.close()

        if response == "Error":
            return False, "Device communication error"
        elif response == "Timeout Error":
            return False, "Device timeout - no response"
        else:
            # Parse model name
            parts = response.split(",")
            if len(parts) >= 2:
                model_name = parts[1].strip()
                return True, model_name
            else:
                return False, "Invalid device response"

    except PermissionError:
        return False, "Permission denied - try running with sudo or check udev rules"
    except Exception as e:
        return False, str(e)
