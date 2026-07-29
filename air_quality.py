"""Utilitas data, fitur, prediksi, dan klasifikasi ISPU DKI Jakarta."""

from pathlib import Path
from datetime import timedelta

import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "datasets" / "data_ispu_clean.csv"

POLLUTANTS = {
    "pm25": "pm_duakomalima",
    "pm10": "pm_sepuluh",
    "so2": "sulfur_dioksida",
    "co": "karbon_monoksida",
    "o3": "ozon",
    "no2": "nitrogen_dioksida",
}

POLLUTANT_LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
    "no2": "NO₂",
}

STATIONS = [
    "DKI1 Bundaran HI",
    "DKI2 Kelapa Gading",
    "DKI3 Jagakarsa",
    "DKI4 Lubang Buaya",
    "DKI5 Kebon Jeruk",
]

KATEGORI_ORDER = [
    "BAIK",
    "SEDANG",
    "TIDAK SEHAT",
    "SANGAT TIDAK SEHAT",
    "BERBAHAYA",
]

KATEGORI_DISPLAY = {
    "BAIK": "Baik",
    "SEDANG": "Sedang (Cukup Sehat)",
    "TIDAK SEHAT": "Tidak Sehat",
    "SANGAT TIDAK SEHAT": "Sangat Tidak Sehat",
    "BERBAHAYA": "Berbahaya",
}

KATEGORI_COLORS = {
    "BAIK": "#2ecc71",
    "SEDANG": "#f1c40f",
    "TIDAK SEHAT": "#e67e22",
    "SANGAT TIDAK SEHAT": "#e74c3c",
    "BERBAHAYA": "#8e44ad",
    "TIDAK ADA DATA": "#95a5a6",
}

# Direct forecasting: horizon H+1 s/d H+7
FORECAST_HORIZONS = range(1, 8)
MAX_FORECAST_HORIZON = 7

BULAN_ID = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}


def format_date_id(ts: pd.Timestamp) -> str:
    """Format tanggal ke bahasa Indonesia, mis. 5 Desember 2025."""
    ts = pd.to_datetime(ts)
    return f"{ts.day} {BULAN_ID[ts.month]} {ts.year}"


def load_raw_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["tanggal_lengkap"] = pd.to_datetime(df["tanggal_lengkap"])
    return df.sort_values(["stasiun", "tanggal_lengkap"]).reset_index(drop=True)


def build_feature_matrix(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Feature engineering identik dengan training_model.py."""
    if df is None:
        df = load_raw_data()
    else:
        df = df.copy()
        df["tanggal_lengkap"] = pd.to_datetime(df["tanggal_lengkap"])
        df = df.sort_values(["stasiun", "tanggal_lengkap"])

    df["bulan_fitur"] = df["tanggal_lengkap"].dt.month
    df["hari_fitur"] = df["tanggal_lengkap"].dt.day
    df["dayofweek"] = df["tanggal_lengkap"].dt.dayofweek

    for col in POLLUTANTS.values():
        for lag in (1, 2, 3, 7, 14, 30):
            df[f"{col}_lag{lag}"] = df.groupby("stasiun")[col].shift(lag)

    df = pd.get_dummies(df, columns=["stasiun"], drop_first=False)
    return df.dropna().reset_index(drop=True)


def kategori_ispu(nilai: float, polutan: str) -> str:
    """Klasifikasi ISPU sederhana (konsisten dengan model training)."""
    if polutan == "co":
        nilai = nilai * 10
    if nilai <= 50:
        return "BAIK"
    if nilai <= 100:
        return "SEDANG"
    if nilai <= 200:
        return "TIDAK SEHAT"
    if nilai <= 300:
        return "SANGAT TIDAK SEHAT"
    return "BERBAHAYA"


def gabungkan_kategori(kategori_list: list[str]) -> str:
    final = "BAIK"
    for level in reversed(KATEGORI_ORDER):
        if level in kategori_list:
            final = level
            break
    return final


def load_models(horizon: int = 1) -> dict:
    """Muat model Random Forest untuk horizon tertentu (H+1 s/d H+7)."""
    if horizon not in FORECAST_HORIZONS:
        raise ValueError(f"Horizon harus antara 1 dan {MAX_FORECAST_HORIZON}, got: {horizon}")

    models = {}
    for name in POLLUTANTS:
        path = ROOT / "models" / f"model_{name}_h{horizon}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Model tidak ditemukan: {path}")
        models[name] = joblib.load(path)
    return models


def get_last_data_date(stasiun: str | None = None) -> pd.Timestamp:
    """Tanggal observasi terakhir (global atau per stasiun)."""
    raw = load_raw_data()
    if stasiun is not None:
        return pd.to_datetime(raw.loc[raw["stasiun"] == stasiun, "tanggal_lengkap"].max())
    return pd.to_datetime(raw["tanggal_lengkap"].max())


def get_forecast_dates() -> list[pd.Timestamp]:
    """Daftar tanggal prediksi H+1 s/d H+7 dari tanggal data terakhir."""
    last_date = get_last_data_date()
    return [last_date + timedelta(days=h) for h in FORECAST_HORIZONS]


def horizon_from_date(pred_date: pd.Timestamp) -> int:
    """Konversi tanggal prediksi ke horizon (H+n)."""
    last_date = get_last_data_date()
    pred_date = pd.to_datetime(pred_date).normalize()
    last_date = last_date.normalize()
    delta = (pred_date - last_date).days
    if delta not in FORECAST_HORIZONS:
        raise ValueError(
            f"Tanggal {pred_date.date()} di luar rentang prediksi "
            f"H+1 s/d H+{MAX_FORECAST_HORIZON} dari data terakhir ({last_date.date()})."
        )
    return delta


def predict_forecast(
    stasiun: str,
    horizon: int,
    models: dict | None = None,
) -> dict:
    """
    Direct forecasting: prediksi polutan dan kategori udara untuk horizon H+n.

    Fitur diambil dari tanggal data terakhir; model H+n dipakai langsung
    tanpa prediksi berantai (bukan recursive).
    """
    if stasiun not in STATIONS:
        raise ValueError(f"Stasiun tidak valid: {stasiun}")
    if horizon not in FORECAST_HORIZONS:
        raise ValueError(f"Horizon harus antara 1 dan {MAX_FORECAST_HORIZON}, got: {horizon}")

    if models is None:
        models = load_models(horizon)

    features = build_feature_matrix()
    station_col = f"stasiun_{stasiun}"
    subset = features[features[station_col] == 1]
    if subset.empty:
        raise ValueError(f"Tidak ada data fitur untuk stasiun {stasiun}")

    row = subset.tail(1)
    last_date = get_last_data_date(stasiun)
    pred_date = last_date + timedelta(days=horizon)

    values = {}
    for name, model in models.items():
        X = row[model.feature_names_in_]
        values[name] = float(model.predict(X)[0])

    kategori_per_polutan = {
        name: kategori_ispu(values[name], name) for name in POLLUTANTS
    }
    status = gabungkan_kategori(list(kategori_per_polutan.values()))

    return {
        "stasiun": stasiun,
        "horizon": horizon,
        "tanggal_terakhir": last_date,
        "tanggal_prediksi": pred_date,
        "nilai": values,
        "kategori_per_polutan": kategori_per_polutan,
        "status": status,
    }


def predict_h1(stasiun: str, models: dict | None = None) -> dict:
    """Prediksi polutan dan kategori udara H+1 untuk satu stasiun."""
    result = predict_forecast(stasiun, horizon=1, models=models)
    # Kompatibilitas: respons predict_h1 tidak menyertakan field horizon
    return {k: v for k, v in result.items() if k != "horizon"}


def predict_next_7_days(stasiun: str) -> list[dict]:
    """Direct forecasting H+1 s/d H+7 untuk satu stasiun."""
    hasil = []
    for horizon in FORECAST_HORIZONS:
        prediksi = predict_forecast(stasiun, horizon)
        hasil.append({
            "hari": horizon,
            "horizon": horizon,
            "tanggal": prediksi["tanggal_prediksi"],
            "nilai": prediksi["nilai"],
            "kategori": prediksi["status"],
            "kategori_per_polutan": prediksi["kategori_per_polutan"],
        })
    return hasil

def ringkasan_stasiun_terkini(df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = load_raw_data()
    latest = df.sort_values("tanggal_lengkap").groupby("stasiun", as_index=False).tail(1)
    return latest[
        [
            "stasiun",
            "tanggal_lengkap",
            "kategori",
            "pm_duakomalima",
            "pm_sepuluh",
            "max",
            "parameter_pencemar_kritis",
        ]
    ].reset_index(drop=True)
