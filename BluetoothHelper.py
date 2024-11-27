import bluetooth
import subprocess

class BluetoothHelper:
    def __init__(self):
        self.nearby_devices = []

    def scan_devices(self, duration=8):
        """
        Scan for Bluetooth devices in range.

        :param duration: Duration in seconds to scan for devices.
        :return: List of tuples with (address, name).
        """
        try:
            self.nearby_devices = bluetooth.discover_devices(
                duration=duration, lookup_names=True,
                                            flush_cache=True, lookup_class=False
            )
            return [(addr, name) for addr, name in self.nearby_devices]
        except bluetooth.BluetoothError as e:
            print(f"Error scanning for devices: {e}")
            return []

    def get_rssi(self, device_address):
        """
        Get the RSSI value of a specific Bluetooth device.

        :param device_address: Bluetooth MAC address of the target device.
        :return: RSSI value as an integer or None if not available.
        """
        try:
            result = subprocess.run(
                ["hcitool", "rssi", device_address],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if "RSSI return value" in output:
                    return int(output.split(":")[-1].strip())
            return None
        except Exception as e:
            print(f"Failed to get RSSI for {device_address}: {e}")
            return None

    def get_devices_with_rssi(self, duration=8):
        """
        Scan for devices and fetch their RSSI values.

        :param duration: Duration in seconds to scan for devices.
        :return: List of tuples with (address, name, RSSI).
        """
        devices_with_rssi = []
        devices = self.scan_devices(duration=duration)

        for addr, name in devices:
            try:
                rssi = self.get_rssi(addr)
                devices_with_rssi.append((addr, name, rssi))
            except Exception as e:
                print(f"Error processing device {addr}: {e}")
                devices_with_rssi.append((addr, name, None))

        return devices_with_rssi

# Example Usage
if __name__ == "__main__":
    bt_helper = BluetoothHelper()

    print("Scanning for Bluetooth devices...")
    devices = bt_helper.get_devices_with_rssi()

    print("\nNearby Devices with RSSI:")
    for addr, name, rssi in devices:
        print(f"Address: {addr}, Name: {name}, RSSI: {rssi}")
