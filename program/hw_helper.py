from constants import *
import RPi.GPIO as GPIO
import time
import serial
import crcmod

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
    num_chars = 24
    while True:
        if ser.in_waiting >= num_chars:
            
            while True:
                start_byte = ser.read(STM32_START_BYTES_SIZE)
                if(start_byte == STM32_START_BYTES):
                    break

            if(start_byte == STM32_START_BYTES):
                data = ser.read(num_chars - STM32_START_BYTES_SIZE)
                crc_value_from_message = data[19:23]
                crc_value_from_message = int.from_bytes(crc_value_from_message, byteorder = 'little')
                message = data[0:18].decode('utf-8')
                crc32 = crcmod.mkCrcFun(poly=0x104c11db7, rev=False, initCrc=0xFFFFFFFF, xorOut=0)
                crc = crc32(data[0:18])
                if(crc_value_from_message != crc):
                    print(RED, "[WARNING]",RESET," Wrong CRC")
                if(crc_value_from_message == crc):
                    print(BLUE, "[INFO]",RESET," Data from stm32 received", message)
                    break

    humidity, temperature = decodeMessage(message)
    return humidity, temperature

def SendCommandToSTM32(port, baudrate, cmd):
    # 0xFFFF is crc16 mock
    f_ackReceived = 0 

    command = 0xCC00DD
    if cmd == SIMPLE_ACK:
        command = command | (SIMPLE_ACK << 8)
        print(YELLOW,"[COMM]",RESET," Command set: ack")
    elif cmd == DO_MEASUREMENT_AFTER_1_HOUR:
        command = command | (DO_MEASUREMENT_AFTER_1_HOUR << 8)
        print(YELLOW,"[COMM]",RESET," Command set: sleep for 1 hour")
    elif cmd == DO_MEASUREMENT_AFTER_3_HOURS:
        command = command | (DO_MEASUREMENT_AFTER_3_HOURS << 8)
        print(YELLOW, "[COMM]",RESET," Command set: sleep for 3 hours")
    elif cmd == DO_MEASUREMENT_AFTER_9_HOURS:
        command = command | (DO_MEASUREMENT_AFTER_9_HOURS << 8)
        print(YELLOW,"[COMM]",RESET," Command set: sleep for 9 hours")
    elif cmd == DO_MEASUREMENT_AFTER_10_MINUTES:
        command = command | (DO_MEASUREMENT_AFTER_10_MINUTES << 8)
        print(YELLOW,"[COMM]",RESET," Command set: sleep for 10 minutes")

    cmd_bytes = command.to_bytes(3, byteorder='big')

    ser = serial.Serial(port, baudrate, timeout = 1) 
    
    for i in range(MAX_WAIT_FOR_ACK_TRIALS):
        if(f_ackReceived == 1):
            break
        ser.write(cmd_bytes) 
        print(YELLOW,"[COMM]",RESET," Send command to STM32")
        start_time = time.time()  # Record the start tim
        actual_time = start_time
        while actual_time - start_time < ACK_WAITING_TIME:
            if ser.in_waiting >= ACK_NUM_CHARS:
                data = ser.read(ACK_NUM_CHARS )
                if(data == command.to_bytes(3, byteorder='big')):
                    print(YELLOW, "[COMM]",RESET," ACK received")
                    f_ackReceived = 1
                    break
            actual_time = time.time()

def GpioInit():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(YELLOW_LED, GPIO.OUT)
    

def WriteRedLED(state):
    if(state == "HIGH"):
        print(BLUE, "[INFO]",RESET," RED LED IS ON")
        GPIO.output(RED_LED, GPIO.HIGH)
    else:
        print(BLUE, "[INFO]",RESET," RED LED IS OFF")
        GPIO.output(RED_LED, GPIO.LOW)
    return 0

def WriteGreenLED(state):
    if(state == "HIGH"):
        print(BLUE, "[INFO]",RESET," GREEN LED IS ON")
        GPIO.output(GREEN_LED, GPIO.HIGH)
    else:
        print(BLUE,"[INFO]",RESET," GREEN LED IS OFF")
        GPIO.output(GREEN_LED, GPIO.LOW)
    return 0

def WriteYellowLED(state):
    if(state == "HIGH"):
        print(BLUE, "[INFO] ",RESET," YELLOW LED IS ON")
        GPIO.output(YELLOW_LED, GPIO.HIGH)
    else:
        print(BLUE, "[INFO] ",RESET," YELLOW LED IS OFF")
        GPIO.output(YELLOW_LED, GPIO.LOW)
    return 0