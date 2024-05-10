from constants import *
import RPi.GPIO as GPIO
import time
import serial

GREEN_LED = 16
YELLOW_LED = 20
RED_LED = 21
ACK_NUM_CHARS = 3
MAX_WAIT_FOR_ACK_TRIALS = 3
STM32_START_BYTES_SIZE = 1
STM32_START_BYTES = b'e'
ACK_WAITING_TIME = 10
RPI_START_BYTE = b'\xcc'
RPI_START_BYTE_SIZE = 1

def decodeMessage(message):
    temperature = message[3:8]
    humidity = message[11:16]
    return humidity, temperature

def WaitForDataFromSTM32(port, baudrate):
    ser = serial.Serial(port, baudrate, timeout = 1) 
    ser.reset_input_buffer()
    num_chars = 20
    while True:
        if ser.in_waiting >= num_chars:
            
            while True:
                start_byte = ser.read(STM32_START_BYTES_SIZE)
                if(start_byte == STM32_START_BYTES):
                    break

            if(start_byte == STM32_START_BYTES):
                data = ser.read(num_chars - STM32_START_BYTES_SIZE)
                message = data.decode('utf-8')
                print("Data from stm32 received: ", message)
                break

    humidity, temperature = decodeMessage(message)
    return humidity, temperature

def SendCommandToSTM32(port, baudrate, cmd):
    # 0xFFFF is crc16 mock
    command = 0xCC00DD
    if cmd == SIMPLE_ACK:
        command = command | (SIMPLE_ACK << 8)
        print("Command set: ack")
    elif cmd == DO_MEASUREMENT_AFTER_1_HOUR:
        command = command | (DO_MEASUREMENT_AFTER_1_HOUR << 8)
        print("Command set: sleep for 1 hour")
    elif cmd == DO_MEASUREMENT_AFTER_3_HOURS:
        command = command | (DO_MEASUREMENT_AFTER_3_HOURS << 8)
        print("Command set: sleep for 3 hours")
    elif cmd == DO_MEASUREMENT_AFTER_9_HOURS:
        command = command | (DO_MEASUREMENT_AFTER_9_HOURS << 8)
        print("Command set: sleep for 9 hours")
    elif cmd == DO_MEASUREMENT_AFTER_10_MINUTES:
        command = command | (DO_MEASUREMENT_AFTER_10_MINUTES << 8)
        print("Command set: sleep for 10 minutes")

    cmd_bytes = command.to_bytes(3, byteorder='big')

    ser = serial.Serial(port, baudrate, timeout = 1) 
    
    for i in range(MAX_WAIT_FOR_ACK_TRIALS):
        ser.write(cmd_bytes) 
        print("Send command to STM32")
        start_time = time.time()  # Record the start tim
        actual_time = start_time
        while actual_time - start_time < ACK_WAITING_TIME:
            if ser.in_waiting >= ACK_NUM_CHARS:
                data = ser.read(ACK_NUM_CHARS )
                print(cmd.to_bytes(3, byteorder='big'))
                if(data == cmd.to_bytes(3, byteorder='big')):
                    print("ACK received")
                    break
            actual_time = time.time()

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