import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv("hasil_perbandingan_model.csv")

# Nama polutan
nama = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
    "no2": "NO₂"
}

# Menggunakan font Times New Roman
plt.rcParams["font.family"] = "Times New Roman"

plt.figure(figsize=(10,6))

# Plot setiap polutan
for polutan in df["Polutan"].unique():

    data = df[df["Polutan"] == polutan]

    plt.plot(
        data["Horizon"],
        data["MAE"],
        marker='o',
        linewidth=2,
        markersize=5,
        label=nama[polutan]
    )

# Judul
plt.title(
    "Perbandingan Nilai MAE\nModel Random Forest pada Setiap Horizon Prediksi",
    fontsize=14,
    weight='bold'
)

# Label sumbu
plt.xlabel("Horizon Prediksi", fontsize=12)
plt.ylabel("Nilai MAE", fontsize=12)

# Tick
plt.xticks(range(1,8))

# Grid
plt.grid(True, linestyle='--', alpha=0.5)

# Legend
plt.legend(
    title="Polutan",
    bbox_to_anchor=(1.02,1),
    loc="upper left"
)

plt.tight_layout()

# Simpan gambar kualitas tinggi
plt.savefig(
    "grafik_mae_random_forest.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()