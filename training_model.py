import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pathlib import Path

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv('datasets/data_ispu_clean.csv')
df['tanggal_lengkap'] = pd.to_datetime(df['tanggal_lengkap'])

# =========================================================
# FITUR WAKTU
# =========================================================
df['bulan_fitur'] = df['tanggal_lengkap'].dt.month
df['hari_fitur'] = df['tanggal_lengkap'].dt.day
df['dayofweek'] = df['tanggal_lengkap'].dt.dayofweek

# =========================================================
# SORT DATA
# =========================================================
df = df.sort_values(by=['stasiun', 'tanggal_lengkap'])

# =========================================================
# POLUTAN
# =========================================================
pollutants = {
    "pm25": "pm_duakomalima",
    "pm10": "pm_sepuluh",
    "so2": "sulfur_dioksida",
    "co": "karbon_monoksida",
    "o3": "ozon",
    "no2": "nitrogen_dioksida"
}

# Direct forecasting: model terpisah untuk H+1 s/d H+7
FORECAST_HORIZONS = range(1, 8)

# =========================================================
# HASIL EVALUASI
# =========================================================
results = []

# =========================================================
# LOOP HORIZON (Direct Forecasting)
# =========================================================
for horizon in FORECAST_HORIZONS:

    print(f"\n{'=' * 50}")
    print(f"===== TRAINING HORIZON H+{horizon} =====")
    print(f"{'=' * 50}")

    # =====================================================
    # LOOP SEMUA POLUTAN
    # =====================================================
    for name, col in pollutants.items():

        print(f"\n----- TRAINING {name.upper()} (H+{horizon}) -----")

        df_temp = df.copy()

        # =================================================
        # LAG FEATURES
        # =================================================
        for lag in [1, 2, 3, 7, 14, 30]:

            df_temp[f'{col}_lag{lag}'] = df_temp.groupby('stasiun')[col].shift(lag)


        # =================================================
        # TARGET — shift(-horizon) untuk direct forecasting
        # =================================================
        df_temp['target'] = df_temp.groupby('stasiun')[col].shift(-horizon)

        # =================================================
        # ENCODING STASIUN
        # =================================================
        df_temp = pd.get_dummies(df_temp, columns=['stasiun'], drop_first=False)


        # =================================================
        # DROP NA
        # =================================================
        df_temp = df_temp.dropna()

        # =================================================
        # FITUR
        # =================================================
        fitur_lag = [c for c in df_temp.columns if 'lag' in c]
        fitur_stasiun = [c for c in df_temp.columns if c.startswith('stasiun_')]

        X = df_temp[fitur_lag + fitur_stasiun + [
            'bulan_fitur',
            'hari_fitur',
            'dayofweek'
        ]]

        y = df_temp['target']

        # =================================================
        # TRAIN TEST SPLIT
        # =================================================
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            shuffle=False
        )

        # =================================================
        # MODEL
        # =================================================
        model = RandomForestRegressor(
            n_estimators=500,
            max_depth=20,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1

        )

        # =================================================
        # TRAINING
        # =================================================

        model.fit(X_train, y_train)

        # =================================================
        # PREDIKSI
        # =================================================

        y_pred = model.predict(X_test)

        # Simpan hasil prediksi H+1 saja (kompatibilitas file lama)
        if horizon == 1:
            hasil_prediksi = pd.DataFrame({
                "Aktual": y_test.values,
                "Prediksi": y_pred
            })
            hasil_prediksi.to_csv(
                f"hasil_prediksi_{name}.csv",
                index=False
            )

        # =================================================
        # EVALUASI
        # =================================================
        mae = mean_absolute_error(y_test, y_pred)
        rmse = mean_squared_error(y_test, y_pred) ** 0.5
        r2 = r2_score(y_test, y_pred)

        print(f"MAE  : {mae:.2f}")
        print(f"RMSE : {rmse:.2f}")
        print(f"R2   : {r2:.4f}")

        # =================================================
        # SIMPAN MODEL
        # =================================================
        MODEL_DIR = Path("models")
        MODEL_DIR.mkdir(exist_ok=True)

        model_filename = MODEL_DIR / f"model_{name}_h{horizon}.pkl"

        joblib.dump(model, model_filename)
        print(f"Model disimpan: {model_filename}")

        # =================================================
        # SIMPAN HASIL EVALUASI
        # =================================================
        results.append([name, horizon, mae, rmse, r2])

# =========================================================
# TABEL HASIL AKHIR
# =========================================================
result_df = pd.DataFrame(
    results,
    columns=['Polutan', 'Horizon', 'MAE', 'RMSE', 'R2']
)

print("\n===== HASIL PERBANDINGAN SEMUA MODEL =====")
print(result_df)
result_df.to_csv("hasil_perbandingan_model.csv", index=False)
print(f"\nSemua model selesai dilatih dan disimpan! ({len(pollutants) * len(FORECAST_HORIZONS)} model)")
