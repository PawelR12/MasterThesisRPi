from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from joblib import dump, load
import numpy as np


def predict_hoarfrost(model, temperature, humidity):
    # Predict hoarfrost probability
    prediction = model.predict(np.array([[temperature, humidity]]))
    return prediction[0]

def main():
   rf_model = load('HoarfrostPrediction.joblib')
   temp = -12
   humid = 99
   print("Random Forest Model Prediction:", predict_hoarfrost(rf_model, temp, humid))

if __name__ == "__main__":
    main()