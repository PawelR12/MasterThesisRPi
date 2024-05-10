import RPi.GPIO as GPIO
import time
import serial

GREEN_LED = 16
YELLOW_LED = 20
RED_LED = 21

def GpioInit():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    

def WriteRedLED(state):
    if(state == "HIGH"):
        print("RED LED IS ON")
        GPIO.output(RED_LED, GPIO.HIGH)
    else:
        print("RED LED IS OFF")
        GPIO.output(RED_LED, GPIO.LOW)
    return 0

def WriteGreenLED(state):
    if(state == "HIGH"):
        print("GREEN LED IS ON")
        GPIO.output(GREEN_LED, GPIO.HIGH)
    else:
        print("GREEN LED IS OFF")
        GPIO.output(GREEN_LED, GPIO.LOW)
    return 0

def WriteYellowLED(state):
    if(state == "HIGH"):
        print("YELLOW LED IS ON")
        GPIO.output(YELLOW_LED, GPIO.HIGH)
    else:
        print("YELLOW LED IS OFF")
        GPIO.output(YELLOW_LED, GPIO.LOW)
    return 0

def SendCommandToSTM32(port="/dev/ttyUSB0", baudrate=115200):
    # 0xFFFF is crc16 mock
    cmd = 0xCC00DD
    cmd = cmd.to_bytes(3, byteorder='big')
    ser = serial.Serial(port, baudrate, timeout = 1) 

    ser.write(cmd) 
    print("Send command to STM32")
 
def main():
    GpioInit()
    WriteGreenLED("0")
    WriteRedLED("0")
    WriteYellowLED("0")
    ser = serial.Serial("/dev/ttyUSB0", 115200, timeout = 1) 
    # SendCommandToSTM32()
    # Define the command integer
    cmd = 0xCC00DD

    # Convert the integer to bytes (3 bytes, big-endian format)
    cmd_bytes = cmd.to_bytes(3, byteorder='big')
    ser.write(cmd_bytes) 
    
    ser.write(b'Hello\n')
    ser.write(0xCC00DD)
    
    ser.write(cmd)
    print("Send command to STM32")
    
if __name__ == "__main__":
    main()
