from constants import *
import RPi.GPIO as GPIO
import time
import serial

GREEN_LED = 16
YELLOW_LED = 20
RED_LED = 21
ACK_NUM_CHARS = 3
MAX_WAIT_FOR_ACK_TRIALS = 3

def decodeMessage(message):
    temperature = message[3:8]
    humidity = message[11:16]
    return humidity, temperature

def WaitForDataFromSTM32(port, baudrate):
    ser = serial.Serial(port, baudrate, timeout = 1) 
    ser.reset_input_buffer()
    num_chars = 19
    while True:
        if ser.in_waiting >= num_chars:
            data = ser.read(num_chars)
            message = data.decode('utf-8')
            print("Data from stm32 received: ", message)
            break
        
    humidity, temperature = decodeMessage(message)
    return humidity, temperature

def SendCommandToSTM32(port, baudrate, cmd):
    # 0xFFFF is crc16 mock
    cmd = 0xCC00DD
    if cmd == SIMPLE_ACK:
        cmd = cmd | (SIMPLE_ACK << 8)
        print("Command set: ack")
    elif cmd == DO_MEASUREMENT_AFTER_1_HOUR:
        cmd = cmd | (DO_MEASUREMENT_AFTER_1_HOUR << 8)
        print("Command set: sleep for 1 hour")
    elif cmd == DO_MEASUREMENT_AFTER_3_HOURS:
        cmd = cmd | (DO_MEASUREMENT_AFTER_3_HOURS << 8)
        print("Command set: sleep for 3 hours")
    elif cmd == DO_MEASUREMENT_AFTER_9_HOURS:
        cmd = cmd | (DO_MEASUREMENT_AFTER_9_HOURS << 8)
        print("Command set: sleep for 9 hours")
    elif cmd == DO_MEASUREMENT_AFTER_10_MINUTES:
        cmd = cmd | (DO_MEASUREMENT_AFTER_10_MINUTES << 8)
        print("Command set: sleep for 10 minutes")

    cmd_bytes = cmd.to_bytes(3, byteorder='big')

    ser = serial.Serial(port, baudrate, timeout = 1) 
    
    for i in range(MAX_WAIT_FOR_ACK_TRIALS):
        ser.write(cmd_bytes) 
        print("Send command to STM32")
        # if ser.in_waiting >= ACK_NUM_CHARS:
        #     data = ser.read(ACK_NUM_CHARS)
        # if data == cmd:
        #     print("ACK received")
        #     break

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