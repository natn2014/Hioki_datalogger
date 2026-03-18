#!/bin/bash

# HIOKI Resistance Meter - Raspberry Pi Auto-Startup Setup Script
# This script installs the application as a systemd service for auto-start on boot
# Usage: sudo bash setup_autostart.sh [install|remove|status|logs]

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_NAME="hioki-meter"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
APP_DIR="/home/pi/hioki_meter"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}This script requires root privileges. Run with: sudo bash setup_autostart.sh${NC}"
    exit 1
fi

install_service() {
    echo -e "${BLUE}Setting up HIOKI Resistance Meter as systemd service...${NC}"
    
    # Check if source service file exists
    if [ ! -f "$SCRIPT_DIR/hioki-meter.service" ]; then
        echo -e "${RED}✗ Service file not found: $SCRIPT_DIR/hioki-meter.service${NC}"
        exit 1
    fi
    
    # Update paths in service file based on current installation
    echo -e "${BLUE}Copying service file to systemd...${NC}"
    cp "$SCRIPT_DIR/hioki-meter.service" "$SERVICE_FILE"
    
    # Set correct permissions
    chmod 644 "$SERVICE_FILE"
    
    # Create virtual environment if not exists
    if [ ! -d "$APP_DIR/venv" ]; then
        echo -e "${BLUE}Creating Python virtual environment...${NC}"
        cd "$APP_DIR"
        python3 -m venv venv
        source venv/bin/activate
        pip install -q -r requirements.txt
        deactivate
    fi
    
    # Reload systemd daemon
    echo -e "${BLUE}Reloading systemd daemon...${NC}"
    systemctl daemon-reload
    
    # Enable service to start on boot
    echo -e "${BLUE}Enabling service for auto-start...${NC}"
    systemctl enable "$SERVICE_NAME"
    
    echo -e "${GREEN}✓ Service installed successfully!${NC}"
    echo -e "${GREEN}✓ Application will auto-start on next boot${NC}"
    echo ""
    echo -e "${YELLOW}Available commands:${NC}"
    echo "  sudo systemctl start $SERVICE_NAME      # Start now"
    echo "  sudo systemctl stop $SERVICE_NAME       # Stop service"
    echo "  sudo systemctl restart $SERVICE_NAME    # Restart service"
    echo "  sudo systemctl status $SERVICE_NAME     # Check status"
    echo "  sudo journalctl -u $SERVICE_NAME -f     # View live logs"
    echo "  sudo bash $0 remove                      # Remove auto-start"
}

remove_service() {
    echo -e "${YELLOW}Removing auto-start service...${NC}"
    
    # Check if service exists
    if [ ! -f "$SERVICE_FILE" ]; then
        echo -e "${YELLOW}! Service not found${NC}"
        exit 0
    fi
    
    # Stop service if running
    echo -e "${BLUE}Stopping service...${NC}"
    systemctl stop "$SERVICE_NAME" || true
    
    # Disable service
    echo -e "${BLUE}Disabling service...${NC}"
    systemctl disable "$SERVICE_NAME" || true
    
    # Remove service file
    echo -e "${BLUE}Removing service file...${NC}"
    rm -f "$SERVICE_FILE"
    
    # Reload systemd daemon
    systemctl daemon-reload
    
    echo -e "${GREEN}✓ Auto-start removed successfully${NC}"
}

status_service() {
    echo -e "${BLUE}HIOKI Resistance Meter Service Status${NC}"
    echo "======================================"
    
    if [ -f "$SERVICE_FILE" ]; then
        echo -e "${GREEN}✓ Service installed${NC}"
        
        if systemctl is-enabled "$SERVICE_NAME" &>/dev/null; then
            echo -e "${GREEN}✓ Service enabled (auto-start on boot)${NC}"
        else
            echo -e "${YELLOW}! Service disabled${NC}"
        fi
        
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            echo -e "${GREEN}✓ Service is running${NC}"
        else
            echo -e "${RED}✗ Service is not running${NC}"
        fi
        
        echo ""
        systemctl status "$SERVICE_NAME" --no-pager || true
    else
        echo -e "${RED}✗ Service not installed${NC}"
        echo "Run 'sudo bash setup_autostart.sh install' to set up auto-start"
    fi
}

view_logs() {
    echo -e "${BLUE}HIOKI Resistance Meter Logs${NC}"
    echo "============================="
    echo "Press Ctrl+C to stop viewing logs"
    echo ""
    journalctl -u "$SERVICE_NAME" -f
}

# Main script logic
case "${1:-status}" in
    install)
        install_service
        ;;
    remove)
        remove_service
        ;;
    status)
        status_service
        ;;
    logs)
        view_logs
        ;;
    *)
        echo "Usage: sudo bash $0 [install|remove|status|logs]"
        echo ""
        echo "Commands:"
        echo "  install  - Install auto-start service"
        echo "  remove   - Remove auto-start service"
        echo "  status   - Check service status"
        echo "  logs     - View live service logs"
        exit 1
        ;;
esac
