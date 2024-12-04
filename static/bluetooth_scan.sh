#!/bin/bash
# bluetooth_scan.sh
# Scanning for Bluetooth devices and publishing to MQTT

echo "Scanning for Bluetooth devices..."

# Run the scan and capture the output using bluetoothctl (or another method that works)
# Example: Using bluetoothctl to scan for devices
scan_output=$(bluetoothctl devices | grep -v "Device" | head -n 10)  # Adjust if necessary

# Publish the devices to the MQTT broker
mosquitto_pub -h localhost -t "home/bluetooth/devices" -m "$scan_output"

echo "Scan completed and data sent to MQTT"
