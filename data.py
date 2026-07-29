import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("datasets/data_ispu_clean.csv")
df["tanggal_lengkap"] = pd.to_datetime(df["tanggal_lengkap"])

# Feature Engineering
df["bulan_fitur"] = df["tanggal_lengkap"].dt.month
df["hari_fitur"] = df["tanggal_lengkap"].dt.day
df["dayofweek"] = df["tanggal_lengkap"].dt.dayofweek

df = df.sort_values(["stasiun", "tanggal_lengkap"])

# Contoh menggunakan PM2.5
for lag in [1,2,3,7,14,30]:
    df[f"pm_duakomalima_lag{lag}"] = (
        df.groupby("stasiun")["pm_duakomalima"].shift(lag)
    )

df["target"] = df.groupby("stasiun")["pm_duakomalima"].shift(-1)

df = pd.get_dummies(df, columns=["stasiun"], drop_first=False)

df = df.dropna()

fitur_lag = [c for c in df.columns if "lag" in c]
fitur_stasiun = [c for c in df.columns if c.startswith("stasiun_")]

X = df[
    fitur_lag +
    fitur_stasiun +
    [
        "bulan_fitur",
        "hari_fitur",
        "dayofweek"
    ]
]

y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    shuffle=False
)

print("===== HASIL PEMBAGIAN DATA =====\n")
print(f"Jumlah Data Keseluruhan : {len(df)}")
print(f"Jumlah Data Latih       : {len(X_train)}")
print(f"Jumlah Data Uji         : {len(X_test)}")