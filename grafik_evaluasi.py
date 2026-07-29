import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================================
# Folder output
# ==========================================================
output_folder = Path("grafik_evaluasi")
output_folder.mkdir(exist_ok=True)

# ==========================================================
# Nama polutan
# ==========================================================
pollutants = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
    "no2": "NO₂"
}

# ==========================================================
# Membaca hasil evaluasi
# ==========================================================
hasil_model = pd.read_csv("hasil_perbandingan_model.csv")

# ==========================================================
# Membuat grafik
# ==========================================================
for key, label in pollutants.items():

    # -----------------------------
    # Load hasil prediksi
    # -----------------------------
    df = pd.read_csv(f"hasil_prediksi_{key}.csv")

    # -----------------------------
    # Ambil nilai R2
    # -----------------------------
    r2 = hasil_model.loc[
        hasil_model["Polutan"] == key,
        "R2"
    ].values[0]

    # -----------------------------
    # Figure
    # -----------------------------
    plt.figure(figsize=(7,7))

    # Scatter
    plt.scatter(
        df["Aktual"],
        df["Prediksi"],
        s=18,
        alpha=0.55,
        label="Data Prediksi"
    )

    # Garis ideal y=x
    nilai_min = min(df["Aktual"].min(), df["Prediksi"].min())
    nilai_max = max(df["Aktual"].max(), df["Prediksi"].max())

    plt.plot(
        [nilai_min, nilai_max],
        [nilai_min, nilai_max],
        linestyle="--",
        linewidth=2,
        color="red",
        label="Prediksi Ideal"
    )

    # Judul
    plt.title(
        f"Perbandingan Nilai Aktual dan Prediksi {label}",
        fontsize=14,
        fontweight="bold"
    )

    # Label
    plt.xlabel("Nilai Aktual", fontsize=11)
    plt.ylabel("Nilai Prediksi", fontsize=11)

    # Grid
    plt.grid(alpha=0.3)

    # Legend
    plt.legend()

    # Tampilkan R²
    plt.text(
        0.05,
        0.95,
        f"$R^2$ = {r2:.3f}",
        transform=plt.gca().transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=dict(
            boxstyle="round",
            facecolor="white",
            alpha=0.8
        )
    )

    plt.tight_layout()

    plt.savefig(
        output_folder / f"grafik_{key}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

print("="*50)
print("Semua grafik evaluasi berhasil dibuat.")
print("Lokasi :", output_folder)
print("="*50)