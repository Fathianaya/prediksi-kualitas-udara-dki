import joblib

model = joblib.load("models/model_pm25_h1.pkl")

print(type(model))

print(model.n_estimators)
import os

print(os.path.getsize("models/model_pm25_h1.pkl")/1024/1024)