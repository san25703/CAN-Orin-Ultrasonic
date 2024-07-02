### CAN-Orin-Ultrasonic

This Python script integrates an ultrasonic distance sensor with a CAN bus system using the NVIDIA AGX Orin GPIO pins. It measures the distance to an object and sends appropriate CAN messages based on the detected distance.

### Prerequisites

To run this script, you need to have the following Python libraries installed:

- **`python-can`**: For CAN bus communication.
- **`RPi.GPIO`**: For GPIO control on the Orin.

Install the required libraries using pip:

```bash
pip install python-can
```
```bash
pip install RPi.GPIO
```

### Description

The script uses an ultrasonic sensor connected to the Orin GPIO pins to measure the distance to an object. It then sends a CAN message to simulate braking behavior when an object is detected.

**Key Functions:**

- **`get_distance()`**: Reads the distance from the ultrasonic sensor.
- **`send_can_message(bus, arbitration_id, data)`**: Sends a CAN message with the specified `arbitration_id` and `data`.
- **`continuous_can_send()`**: Main loop that continuously reads distance and sends CAN messages based on the distance measurement.

**CAN Messages:**

- **Brake (Object Detected)**: ID: `0x131`, Data: `[0x03, 0xC8, 0x00, 0x01, 0x00, 0x00, seventh_byte, 0x00]`
  ```python
  if distance < 100:
      if not object_detected:
          object_detected = True
          object_just_left = False
          data_brake = [0x03, 0xC8, 0x00, 0x01, 0x00, 0x00, seventh_byte, 0x00]
          data_brake[7] = data_brake[0] ^ data_brake[1] ^ data_brake[2] ^ data_brake[3] ^ data_brake[4] ^ data_brake[5] ^ data_brake[6]
          send_can_message(bus, 0x131, data_brake)
  ```

- **Brake Release (Object No Longer Detected)**: ID: `0x131`, Data: `[0x03, 0xC8, 0x00, 0x02, 0x00, 0x00, seventh_byte, 0x00]`
  ```python
  if distance >= 100:
      if object_detected and not object_just_left:
          object_detected = False
          object_just_left = True
          data_brake = [0x03, 0xC8, 0x00, 0x02, 0x00, 0x00, seventh_byte, 0x00]
          data_brake[7] = data_brake[0] ^ data_brake[1] ^ data_brake[2] ^ data_brake[3] ^ data_brake[4] ^ data_brake[5] ^ data_brake[6]
          send_can_message(bus, 0x131, data_brake)
  ```

**Note**: The `seventh_byte` is updated in each loop iteration and used to generate a simple checksum for the CAN message.

### GPIO Configuration

- **TRIG_PIN (GPIO 33)**: Trigger pin for the ultrasonic sensor.
- **ECHO_PIN (GPIO 31)**: Echo pin for the ultrasonic sensor.

### Usage

1. **Connect the Ultrasonic Sensor**:
   - **TRIG** to GPIO 33 on the Orin
   - **ECHO** to GPIO 31 on the Orin

![Orin PinOut](https://github.com/san25703/CAN-Orin-Ultrasonic/blob/main/Orin%20Pinout.png?raw=true)


2. **Configure the CAN Channel**:
   - Update the `channel` argument in the `can.interface.Bus` instantiation to match your PCAN-USB hardware port.

3. **Run the Script**:
   - Execute the script to start measuring distance and sending CAN messages. The script runs continuously and sends messages every 20 ms based on the distance measurement.

### Example Configuration

For `PCAN-USB X6` with CAN3 port:

```python
bus = can.interface.Bus(channel='PCAN_USBBUS2', interface='pcan', bitrate=500000)
```

### Example Output

When an object is detected within 100 units:

```
Distance: 75.00 units
Message sent: ID=0x131, Data: 03 C8 00 01 00 00 00 00
```

When the object is no longer detected:

```
Distance: 105.00 units
Message sent: ID=0x131, Data: 03 C8 00 02 00 00 00 00
```

### Resources

- [python-can Documentation](https://python-can.readthedocs.io/)
- [RPi.GPIO Documentation](https://sourceforge.net/projects/raspberry-gpio-python/)
