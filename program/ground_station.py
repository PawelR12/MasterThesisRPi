# Ground station program

# Start
'''
1) Receive data from stm32
2) retrieve hour
3) save data to buffer with hour
    if it is 3rd postion in buffer:
    4) Send command (which is already ack)
    --- COMMAND -> 4 bytes
    1st byte -> 0xCC start byte
    2nd byte -> command
    3 and 4rd byte -> crc16
    5) calculate actual hoarfrost danger
        if danger exist:
        4a) light up red LED
        4b) send data to stm32 to do a measurement after 10 minutes 
        4c) set "COMMAND SENDED" flag
    6) predict for next 6 hours
        if danger is higher than X:
            7a) light up a YELLOW LED
            if flag "COMMAND SENDED" is disabled
                7b) send command to stm32 to do a measurement after 3 hours
        if danger is lower than X:
            if flag "COMMAND SENDED" is disabled
                7c) send command to stm32 to do a measurement after 6 hours
    
'''



from time import gmtime, strftime
import time 
import numpy as np
from constants import *
import hw_helper
import predictions_func as pf

def main():
    m_MyList = []
    m_OperationStageFlag = ONE_HOUR_1ST_DATA
    m_HoarfrostPossibility = 0
    m_PredictedHoarfrostDanger = 0
    f_CmdSended = 0

    while True:
        humidity, temperature = hw_helper.WaitForDataFromSTM32('/dev/ttyUSB0', 115200)
        timeElapsedFromEpoch = time.time() # epoch is Januray 1st, 1970 00:00:00 
        act_time = strftime("%H %M %m", 
             gmtime(timeElapsedFromEpoch))
        hour, minutes, month = act_time.split()
        month = int(month)
        if( month > 4 and month < 8):
            print("During summer hoarfrost prediction is not calculated - termination")
            exit()
        
        hour = int(hour)
        minutes = int(minutes)
        if int(minutes) > 30:
            hour = ((int)(hour)+1)
        print("Hour: ",int(hour), "Humidity: ", humidity, "Temperature: ", temperature)

        if m_OperationStageFlag == ONE_HOUR_1ST_DATA:
            m_MyList.clear()
            m_MyList.append([hour, humidity, temperature])
            m_OperationStageFlag = ONE_HOUR_2ND_DATA
            hw_helper.SendCommandToSTM32(DO_MEASUREMENT_AFTER_1_HOUR)

        elif m_OperationStageFlag == ONE_HOUR_2ND_DATA:
            m_MyList.append([hour, humidity, temperature])
            m_OperationStageFlag = ONE_HOUR_3RD_DATA
            hw_helper.SendCommandToSTM32(DO_MEASUREMENT_AFTER_1_HOUR)

        elif m_OperationStageFlag == ONE_HOUR_3RD_DATA:
            m_MyList.append([hour, humidity, temperature])
            m_HoarfrostPossibility = pf.CalculateCurrentHoarFrostDanger(m_MyList[2])
            print("Current Hoarfrost Possibiility is ", m_HoarfrostPossibility)

            if m_HoarfrostPossibility > HOARFROST_CURRENT_DANGER_LIMIT:
                hw_helper.TurnOnRedLED()
                hw_helper.SendCommandToSTM32(DO_MEASUREMENT_AFTER_10_MINUTES)
                f_CmdSended = 1
                m_OperationStageFlag = TEN_MINUTES_DATA
            
            m_PredictedTempHumidity = pf.PredictHoarfrostPossibilityForNext6Hours(m_MyList)
            print("Predicted Temp, Humidity for next hours")
            print(m_PredictedTempHumidity)
            pf.displayPredictedTempHumidity(m_PredictedTempHumidity, hour)
            m_PredictedHoarfrostDanger = pf.calculatePredictedHoarfrostPossibility(m_PredictedTempHumidity)
            print(m_PredictedHoarfrostDanger)

            m_PredictedHoarfrostDanger_SUM = np.sum(m_PredictedHoarfrostDanger)
            m_PredictedHoarfrostDanger_MAX = np.max(m_PredictedHoarfrostDanger)
            if (m_PredictedHoarfrostDanger_SUM/6 > HOARFROST_PREDICTED_DANGER_AVG_LIMIT or m_PredictedHoarfrostDanger_MAX > HOARFROST_PREDICTED_DANGER_MAX_LIMIT ):
                hw_helper.TurnOnYellowLED()
                if not f_CmdSended:
                    hw_helper.SendCommandToSTM32(DO_MEASUREMENT_AFTER_3_HOURS)
                    m_OperationStageFlag = ONE_HOUR_1ST_DATA
            else:
                if not f_CmdSended:
                    hw_helper.SendCommandToSTM32(DO_MEASUREMENT_AFTER_9_HOURS)
                    m_OperationStageFlag = ONE_HOUR_1ST_DATA

        elif m_OperationStageFlag == TEN_MINUTES_DATA:
            m_MyList.append([temperature, humidity, hour])
            m_HoarfrostPossibility = pf.CalculateCurrentHoarFrostDanger(m_MyList[2])
            print("Ten minutes data", m_HoarfrostPossibility)

if __name__ == "__main__":
    main()