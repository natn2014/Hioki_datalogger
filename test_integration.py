# coding: UTF-8

"""
Integration test script for HIOKI Resistance Meter application.
Verifies all components can be imported and basic functionality works.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("[TEST] Testing imports...")
    
    try:
        from port_scanner import get_all_ports, scan_ports, verify_hioki_connection
        print("  ✓ port_scanner imported")
    except ImportError as e:
        print(f"  ✗ port_scanner import failed: {e}")
        return False
    
    try:
        from measurement_worker import MeasurementWorker
        print("  ✓ measurement_worker imported")
    except ImportError as e:
        print(f"  ✗ measurement_worker import failed: {e}")
        return False
    
    try:
        from usb_rs import Usb_rs
        print("  ✓ usb_rs imported")
    except ImportError as e:
        print(f"  ✗ usb_rs import failed: {e}")
        return False
    
    try:
        from insert_resistance2db import insert_to_mssql
        print("  ✓ insert_resistance2db imported")
    except ImportError as e:
        print(f"  ✗ insert_resistance2db import failed: {e}")
        return False
    
    try:
        from ui_UI_Resistance import Ui_Dialog
        print("  ✓ ui_UI_Resistance imported")
    except ImportError as e:
        print(f"  ✗ ui_UI_Resistance import failed: {e}")
        return False
    
    return True

def test_port_scanner():
    """Test port scanning functionality."""
    print("\n[TEST] Testing port scanner...")
    
    try:
        from port_scanner import get_all_ports, scan_ports
        
        ports = get_all_ports()
        print(f"  ✓ Found {len(ports)} available port(s): {ports}")
        
        # Try to scan for HIOKI
        port, model = scan_ports()
        if port:
            print(f"  ✓ HIOKI device found: {model} on {port}")
        else:
            print(f"  ! No HIOKI device detected (normal if not connected)")
        
        return True
    except Exception as e:
        print(f"  ✗ Port scanner error: {e}")
        return False

def test_measurement_worker():
    """Test measurement worker instantiation."""
    print("\n[TEST] Testing measurement worker...")
    
    try:
        from measurement_worker import MeasurementWorker
        
        worker = MeasurementWorker()
        print(f"  ✓ MeasurementWorker instantiated")
        print(f"  ✓ Measurement interval: {worker.measurement_interval}s")
        print(f"  ✓ Timeout: {worker.timeout}s")
        print(f"  ✓ Max retries: {worker.max_retries}")
        
        return True
    except Exception as e:
        print(f"  ✗ MeasurementWorker error: {e}")
        return False

def test_usb_rs():
    """Test USB/RS serial class."""
    print("\n[TEST] Testing USB/RS class...")
    
    try:
        from usb_rs import Usb_rs
        
        ser = Usb_rs(gui=False)
        print(f"  ✓ Usb_rs instantiated")
        print(f"  ✓ Serial port initialized (closed state)")
        
        return True
    except Exception as e:
        print(f"  ✗ Usb_rs error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("HIOKI Resistance Meter - Integration Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Port Scanner", test_port_scanner()))
    results.append(("Measurement Worker", test_measurement_worker()))
    results.append(("USB/RS Serial", test_usb_rs()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    all_pass = all(result for _, result in results)
    
    print("=" * 60)
    if all_pass:
        print("✓ All tests passed! Application is ready to run.")
        print("\nTo start the application:")
        print("  python main.py")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
