import tensorflow as tf
import numpy as np
import joblib
from joblib import dump, load
from sklearn.exceptions import DataConversionWarning
import warnings
import os

warnings.filterwarnings(action = 'ignore', category=UserWarning, module='sklearn')
interpreter = tf.lite.Interpreter(model_path='/home/user/Desktop/MasterThesis/program/model.tflite')
interpreter.allocate_tensors()
scaler = joblib.load('/home/user/Desktop/MasterThesis/program/scaler.save')
rf_model = load('/home/user/Desktop/MasterThesis/program/HoarfrostPrediction.joblib')

def CalculateCurrentHoarFrostDanger(data):
    temperature = data[2]
    humidity = data[1]
    prediction = rf_model.predict(np.array([[temperature, humidity]])) * 10
    return prediction[0]

def RawCalculateHoarfrostDanger(humidity, temperature):
    prediction = rf_model.predict(np.array([[temperature, humidity]]))
    return prediction[0]

def PredictHoarfrostPossibilityForNext6Hours(l_List):
    current_time, humidtidy, temperature, humidtidy_1H_ago, temperature_1H_ago, humidtidy_2H_ago, temperature_2H_ago =_parse_list(l_List)
    predictions = _predict_next_hours(current_time, humidtidy, temperature, humidtidy_1H_ago, temperature_1H_ago, humidtidy_2H_ago, temperature_2H_ago)
    return predictions

def displayPredictedTempHumidity(predictions, time):
    
    for i in range(6):
        if time == 23:
            time = 0
        else:
            time = time + 1
        print("Time: ", time, "Humidity: ", predictions[0][2*i], "Temperature: ", predictions[0][2*i+1])
  
def calculatePredictedHoarfrostPossibility(predictions):
    HoarfrostList = []
    for i in range(6):
        HoarfrostList.append(RawCalculateHoarfrostDanger(predictions[0][2*i],predictions[0][2*i+1]))
    return HoarfrostList

# PRIVATE FUNCTIONS (USED ONLY HERE)
def _compute(interpreter, X):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_data = np.array(X, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

def _predict_next_hours(time, humidity, temperature, last_humidity, last_temperature, last_humidity_2, last_temperature_2):
    hour_sin = np.sin(2 * np.pi * time / 24.0)
    hour_cos = np.cos(2 * np.pi * time / 24.0)
    X = [[humidity, temperature, hour_sin, hour_cos, last_humidity,  last_temperature, last_humidity_2, last_temperature_2]]
    predictions = [[0,0] for x in range(6)]
    X_scaled = scaler.transform(X)
    predictions = _compute(interpreter, X_scaled)
    return predictions

def _parse_list(l_List):
    humidtidy = l_List[0][1]
    humidtidy_1H_ago = l_List[1][1]
    humidtidy_2H_ago = l_List[2][1]
    temperature = l_List[0][2]
    temperature_1H_ago = l_List[1][2]
    temperature_2H_ago = l_List[2][2]
    current_time = l_List[2][0]
    return current_time, humidtidy, temperature, humidtidy_1H_ago, temperature_1H_ago, humidtidy_2H_ago, temperature_2H_ago
