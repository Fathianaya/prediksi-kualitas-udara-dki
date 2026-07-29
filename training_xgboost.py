import pandas as pd
import joblib

from xgboost import XGBRegressor

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# =========================================================
# MEMBACA DATASET
# =========================================================

df = pd.read_csv(
    'datasets/data_ispu_clean.csv'
)

# =========================================================
# KONVERSI TANGGAL
# =========================================================

df['tanggal_lengkap'] = pd.to_datetime(
    df['tanggal_lengkap']
)

# =========================================================
# FITUR WAKTU
# =========================================================

df['bulan_fitur'] = (
    df['tanggal_lengkap'].dt.month
)

df['hari_fitur'] = (
    df['tanggal_lengkap'].dt.day
)

df['dayofweek'] = (
    df['tanggal_lengkap'].dt.dayofweek
)

# =========================================================
# SIMPAN NAMA STASIUN
# =========================================================

stasiun_asli = df['stasiun']

# =========================================================
# FITUR LAG PER STASIUN
# =========================================================

df = df.sort_values(
    by=['stasiun', 'tanggal_lengkap']
)

kolom_polutan = [

    'pm_sepuluh',
    'pm_duakomalima',
    'sulfur_dioksida',
    'karbon_monoksida',
    'ozon',
    'nitrogen_dioksida'
]

for kolom in kolom_polutan:

    for lag in [1, 2, 3, 7, 14, 30]:

        df[f'{kolom}_lag{lag}'] = (
            df.groupby('stasiun')[kolom]
            .shift(lag)
        )

# =========================================================
# TARGET H+1
# =========================================================

df['target_pm25'] = (
    df.groupby('stasiun')['pm_duakomalima']
    .shift(-1)
)

# =========================================================
# ENCODING STASIUN
# =========================================================

df = pd.get_dummies(
    df,
    columns=['stasiun']
)

# =========================================================
# HAPUS NaN
# =========================================================

print("\n===== JUMLAH DATA SEBELUM DROP =====")
print(len(df))

df = df.dropna()

print("\n===== JUMLAH DATA SETELAH DROP =====")
print(len(df))

# =========================================================
# FITUR
# =========================================================

fitur_lag = [

    col
    for col in df.columns
    if 'lag' in col
]

fitur_stasiun = [

    col
    for col in df.columns
    if col.startswith('stasiun_')
]

fitur = (

    fitur_lag +

    fitur_stasiun +

    [
        'bulan_fitur',
        'hari_fitur',
        'dayofweek'
    ]
)

X = df[fitur]

y = df['target_pm25']

# =========================================================
# SPLIT DATA
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    shuffle=False
)

# =========================================================
# MODEL XGBOOST
# =========================================================

model = XGBRegressor(

    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# =========================================================
# TRAINING
# =========================================================

print("\nTraining XGBoost...")

model.fit(
    X_train,
    y_train
)

print("Training Selesai")

# =========================================================
# PREDIKSI
# =========================================================

y_pred = model.predict(
    X_test
)

# =========================================================
# EVALUASI
# =========================================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = (
    mean_squared_error(
        y_test,
        y_pred
    )
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)

print("\n===== HASIL EVALUASI XGBOOST =====")

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"R2   : {r2:.4f}")

# =========================================================
# SIMPAN MODEL
# =========================================================

joblib.dump(
    model,
    'model_pm25_xgboost.pkl'
)

print("\nModel berhasil disimpan")