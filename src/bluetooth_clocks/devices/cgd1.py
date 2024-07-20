import os
from struct import pack
from time import time
from bluetooth_clocks.devices.qingping import CGC1
from bleak import BleakClient

# Define UUIDs and characteristics
KEY_COMMAND = b"\x11\x01"
AUTH_COMMAND = b"\x11\x02"


def generate_key():
    """Generate a new 128-bit key."""
    return os.urandom(16)


def get_bytes_from_time(timestamp, timezone_offset_hours):
    """Generate the bytes to set the time on the Qingping BT Clock Lite."""
    # Convert timezone offset from hours to seconds
    timezone_offset_seconds = timezone_offset_hours * 3600
    adjusted_timestamp = int(timestamp + timezone_offset_seconds)
    # Return the packed byte format
    return pack(
        "<BBL",  # Format string: two bytes, then an unsigned long
        0x05,
        0x09,
        adjusted_timestamp,
    )


async def write_to_characteristic(client, command, data):
    """Write data to a Bluetooth characteristic."""
    await client.write_gatt_char(CGC1.CHAR_UUID, command + data, response=True)


async def sync_time(device_address, offset=0):
    async with BleakClient(device_address) as client:
        # Generate a new key
        key = generate_key()
        key_hex = key.hex()
        print(f"Generated key: {key_hex}")

        # Write the new key
        print("Setting new key...")
        await write_to_characteristic(client, KEY_COMMAND, key)

        # Authenticate the new key
        print("Authenticating key...")
        await write_to_characteristic(client, AUTH_COMMAND, key)

        # Get current time and convert to bytes
        timestamp = time()  # Current time in seconds since epoch
        time_bytes = get_bytes_from_time(timestamp, timezone_offset_hours=offset)

        # Send the time command
        print("Synchronizing time...")
        await write_to_characteristic(
            client, b"", time_bytes
        )  # Empty command, only data is needed here

        print("Time synchronization complete.")
