from constants import *
import RPi.GPIO as GPIO
import time
import serial

GREEN_LED = 16
YELLOW_LED = 20
RED_LED = 21
ACK_NUM_CHARS = 3

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
        print("Command: ACK send to STM32")
        cmd = cmd | (SIMPLE_ACK << 8 )
    elif cmd == DO_MEASUREMENT_AFTER_1_HOUR:
        print("Command: 1 hour sleep send to STM32")
        cmd = cmd | (DO_MEASUREMENT_AFTER_1_HOUR << 8 )
    elif cmd == DO_MEASUREMENT_AFTER_3_HOURS:
        print("Command: 3 hour sleep send to STM32")
        cmd = cmd | (DO_MEASUREMENT_AFTER_3_HOURS << 8 )
    elif cmd == DO_MEASUREMENT_AFTER_9_HOURS:
        cmd = cmd | (DO_MEASUREMENT_AFTER_9_HOURS << 8 )
    elif cmd == DO_MEASUREMENT_AFTER_10_MINUTES:
        cmd = cmd | (DO_MEASUREMENT_AFTER_10_MINUTES << 8 )

    ser = serial.Serial(port, baudrate, timeout = 1) 
    ser.write(0xAA)  # Send a string repeatedly
    if ser.in_waiting >= ack_num_chars:
            data = ser.read(num_chars)

    while True:
        if ser.in_waiting >= num_chars:
            data = ser.read(num_chars)
            message = data.decode('utf-8')
            print("Data from stm32 received: ", message)
            break
    # add wait for ack


def GpioInit():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    

def TurnOnRedLED():
    print("RED LED IS ON")
    GPIO.output(RED_LED, GPIO.HIGH)
    return 0

def TurnOnGreenLED():
    print("GREEN LED IS ON")
    GPIO.output(GREEN_LED, GPIO.HIGH)
    return 0

def TurnOnYellowLED():
    print("YELLOW LED IS ON")
    GPIO.output(YELLOW_LED, GPIO.HIGH)
    return 0
