import pandas as pd
import matplotlib.pyplot as plt

# ==========================
# Data Evaluasi H+1
# ==========================

data = {
    "Parameter": ["PM2.5", "PM10", "SO₂", "CO", "O₃", "NO₂"],
    "R2": [0.573, 0.475, 0.512, 0.559, 0.009, 0.732]
}

df = pd.DataFrame(data)

# Urutkan dari terbesar ke terkecil
df = df.sort_values(by="R2", ascending=False)

# ==========================
# Membuat Grafik
# ==========================

plt.figure(figsize=(8,5))

bars = plt.bar(df["Parameter"], df["R2"])

# Menampilkan nilai di atas batang
for bar in bars:
    tinggi = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        tinggi + 0.015,
        f"{tinggi:.3f}",
        ha="center",
        fontsize=10
    )

plt.title("Perbandingan Nilai Koefisien Determinasi (R²)\nModel Random Forest pada Horizon Prediksi H+1",
          fontsize=13)

plt.xlabel("Parameter Pencemar")
plt.ylabel("Nilai R²")

plt.ylim(0, 0.8)

plt.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()

plt.savefig(
    "grafik_r2_h1.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()