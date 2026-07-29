import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# Load hasil evaluasi
# ==========================
df = pd.read_csv("hasil_perbandingan_model.csv")

# ==========================
# Nama polutan
# ==========================
nama_polutan = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
    "no2": "NO₂"
}

# ==========================
# Ukuran gambar
# ==========================
plt.figure(figsize=(10,6))

# ==========================
# Plot setiap polutan
# ==========================
for polutan in nama_polutan.keys():

    data = df[df["Polutan"] == polutan]

    plt.plot(
        data["Horizon"],
        data["R2"],
        marker='o',
        linewidth=2,
        markersize=6,
        label=nama_polutan[polutan]
    )

# ==========================
# Judul dan Label
# ==========================
plt.title(
    "Perbandingan Nilai Koefisien Determinasi (R²)\n"
    "Model Random Forest pada Setiap Horizon Prediksi",
    fontsize=14,
    weight='bold'
)

plt.xlabel("Horizon Prediksi")
plt.ylabel("Nilai R²")

plt.xticks(range(1,8))
plt.grid(True, linestyle="--", alpha=0.5)

plt.legend(title="Polutan")

plt.tight_layout()

# ==========================
# Simpan gambar
# ==========================
plt.savefig(
    "grafik_r2_keseluruhan.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()