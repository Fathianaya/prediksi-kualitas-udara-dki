import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# MEMBACA HASIL EVALUASI MODEL
# ==========================================================
df = pd.read_csv("hasil_perbandingan_model.csv")

# ==========================================================
# MENGUBAH NAMA POLUTAN AGAR SESUAI PENULISAN ILMIAH
# ==========================================================
label_polutan = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "so2": "SO₂",
    "co": "CO",
    "o3": "O₃",
    "no2": "NO₂"
}

df["Polutan"] = df["Polutan"].map(label_polutan)

# ==========================================================
# URUTKAN BERDASARKAN NILAI R²
# ==========================================================
df = df.sort_values(by="R2", ascending=True)

# ==========================================================
# MEMBERIKAN WARNA BERBEDA
# ==========================================================
colors = []

for polutan in df["Polutan"]:

    if polutan == "NO₂":
        colors.append("forestgreen")      # terbaik

    elif polutan == "O₃":
        colors.append("firebrick")        # terendah

    else:
        colors.append("steelblue")        # lainnya

# ==========================================================
# MEMBUAT GRAFIK
# ==========================================================
plt.figure(figsize=(10,6))

bars = plt.barh(
    df["Polutan"],
    df["R2"],
    color=colors
)

# ==========================================================
# MENAMPILKAN NILAI R² DI UJUNG BATANG
# ==========================================================
for bar in bars:

    value = bar.get_width()

    plt.text(
        value + 0.01,
        bar.get_y() + bar.get_height()/2,
        f"{value:.3f}",
        va="center",
        fontsize=12,
        fontweight="bold"
    )

# ==========================================================
# PENGATURAN TAMPILAN
# ==========================================================
plt.xlim(0,1)

plt.xlabel(
    "Nilai Koefisien Determinasi (R²)",
    fontsize=13
)

plt.ylabel(
    "Parameter Polutan",
    fontsize=13
)

plt.title(
    "Perbandingan Koefisien Determinasi (R²)\nModel Random Forest untuk Setiap Parameter Polutan",
    fontsize=16,
    fontweight="bold"
)

plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.grid(
    axis="x",
    linestyle="--",
    alpha=0.35
)

# ==========================================================
# MENYIMPAN GAMBAR
# ==========================================================
plt.tight_layout()

plt.savefig(
    "grafik_perbandingan_r2.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()