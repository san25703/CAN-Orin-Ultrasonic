import time
import can
import RPi.GPIO as GPIO  # Import GPIO library for Raspberry Pi

# GPIO setup for ultrasonic sensor
TRIG_PIN = 33
ECHO_PIN = 31

GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Function to read distance from ultrasonic sensor
def get_distance():
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()

    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

# Function to send CAN message using python-can
def send_can_message(bus, arbitration_id, data):
    message = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
    try:
        bus.send(message)
        print(f"Message sent: ID=0x{arbitration_id:X}, Data: {' '.join(f'{byte:02X}' for byte in data)}")
    except can.CanError as e:
        print(f"Message not sent: {e}")

def continuous_can_send():
    try:
        bus = can.interface.Bus(channel='PCAN_USBBUS2', interface='pcan', bitrate=500000)
    except can.CanError as e:
        print(f"Failed to initialize CAN bus: {e}")
        return

    seventh_byte = 0x00
    object_detected = False
    object_just_left = False

    try:
        while True:
            distance = get_distance()
            print(f"Distance: {distance} units")

            if distance < 100:
                if not object_detected:
                    object_detected = True
                    object_just_left = False
                    data_brake = [0x03, 0xC8, 0x00, 0x01, 0x00, 0x00, seventh_byte, 0x00]
                    data_brake[7] = data_brake[0] ^ data_brake[1] ^ data_brake[2] ^ data_brake[3] ^ data_brake[4] ^ data_brake[5] ^ data_brake[6]
                    send_can_message(bus, 0x131, data_brake)
            else:
                if object_detected and not object_just_left:
                    object_detected = False
                    object_just_left = True
                    data_brake = [0x03, 0xC8, 0x00, 0x02, 0x00, 0x00, seventh_byte, 0x00]
                    data_brake[7] = data_brake[0] ^ data_brake[1] ^ data_brake[2] ^ data_brake[3] ^ data_brake[4] ^ data_brake[5] ^ data_brake[6]
                    send_can_message(bus, 0x131, data_brake)

            seventh_byte = (seventh_byte + 1) % 0x10
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        bus.shutdown()
        GPIO.cleanup()



if __name__ == "__main__":
    continuous_can_send()

