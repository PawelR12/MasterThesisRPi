import tensorflow as tf
import numpy as np
import joblib
from sklearn.exceptions import DataConversionWarning
import warnings

def predict_next_hours(interpreter, scaler, time, humidity, temperature, last_humidity, last_temperature, last_humidity_2, last_temperature_2):
    hour_sin = np.sin(2 * np.pi * time / 24.0)
    hour_cos = np.cos(2 * np.pi * time / 24.0)
    X = [[humidity, temperature, hour_sin, hour_cos, last_humidity,  last_temperature, last_humidity_2, last_temperature_2]]
    predictions = [[0,0] for x in range(6)]
    for i in range(6):
        X_scaled = scaler.transform(X)
        predicted_val_array = compute(interpreter, X_scaled)
        predictions[i][0] = predicted_val_array[0,0]
        predictions[i][1] = predicted_val_array[0,1]

        #Reasing after compute
        time = time + 1
        hour_sin = np.sin(2 * np.pi * time / 24.0)
        hour_cos = np.cos(2 * np.pi * time / 24.0)

        last_humidity_2 = last_humidity
        last_temperature_2 = last_temperature
        last_humidity = humidity
        last_temperature = temperature
        humidity = predictions[i][0]
        temperature = predictions[i][1]
        X = [[humidity, temperature, hour_sin, hour_cos, last_humidity,  last_temperature, last_humidity_2, last_temperature_2]]
        print(X)
    print(predictions)
    
    # X = predictions[0][0] + predictions [0][1] + X
    # X_scaled = scaler.transform(X)
    # print(X)
    # predictions[1] = compute(interpreter, X_scaled)
    
def compute(interpreter, X):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_data = np.array(X, dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])
def main():
    warnings.filterwarnings(action = 'ignore', category=UserWarning, module='sklearn')
    #load model
    interpreter = tf.lite.Interpreter(model_path='model.tflite')
    scaler = joblib.load('scaler.save')
    interpreter.allocate_tensors()
    output_data = predict_next_hours(interpreter, scaler, 2, 97.33, -1.6, 97.44, -0.3, 97.5, 0.1)
    # print(output_data)
if __name__ == "__main__":
    main()