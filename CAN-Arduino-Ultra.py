import serial
import time
import can

# Function to send CAN message using python-can
def send_can_message(bus, arbitration_id, data):
    message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
    try:
        bus.send(message)
        print(f"Message sent: {message}")
    except can.CanError as e:
        print(f"Message not sent: {e}")

# Function to monitor sensor data and send CAN message based on condition
def monitor_sensor_and_send():
    # Set up serial connection to Arduino
    ser = serial.Serial('COM11', 9600)  # Adjust COM port as needed

    # Try to create a CAN bus instance
    try:
        bus = can.interface.Bus(channel='PCAN_USBBUS1', interface='pcan', bitrate=500000)
    except can.CanError as e:
        print(f"Failed to initialize CAN bus: {e}")
        return

    # Define condition
    threshold_distance = 100  # Send CAN message if distance is less than this value
    send_message = False  # Flag to control sending CAN message
    seventh_byte = 0x00  # Initialize 7th byte

    try:
        while True:
            # Read distance from serial
            if not send_message and ser.in_waiting > 0:
                distance_str = ser.readline().decode('utf-8').strip()
                if distance_str.isdigit():
                    distance = int(distance_str)
                    print(f"Distance: {distance} cm")

                    # Check condition to start sending CAN messages
                    if distance < threshold_distance:
                        print("Condition met! Starting to send CAN messages.")
                        send_message = True

            # Send CAN messages continuously if send_message flag is True
            if not send_message:
                # Calculate 8th byte as XOR of all other bytes

                #Brake 
                #eighth_byte = 0x03 ^ 0xC8 ^ 0x00 ^ 0x02 ^ 0x00 ^ 0x00 ^ seventh_byte
                #send_can_message(bus, 0x131, [0x03, 0xC8, 0x00, 0x02, 0x00, 0x00, seventh_byte, eighth_byte])
                
                eighth_byte = 0x11 ^ 0x64 ^ 0x00 ^ 0x00 ^ 0x0A ^ 0x00 ^ seventh_byte
                send_can_message(bus, 0x132, [0x11, 0xFF, 0x00, 0x00, 0x0A, 0x00, seventh_byte, eighth_byte])
                
                #Velocity
                eighth_byte = 0x11 ^ 0x64 ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x00 ^ seventh_byte
                send_can_message(bus, 0x130, [0x11, 0x64, 0x00, 0x00, 0x00, 0x00, seventh_byte, eighth_byte])
                
                # Send CAN message
                

                # Increment 7th byte and reset to 0x00 if it reaches 0x0F
                seventh_byte = (seventh_byte + 1) % 16

                # Sleep for a short duration to avoid flooding the CAN bus
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()
        bus.shutdown()

if __name__ == "__main__":
    monitor_sensor_and_send()
