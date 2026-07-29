"""Skrip CLI prediksi kualitas udara H+1 s/d H+7 DKI Jakarta (Direct Forecasting)."""

import pandas as pd

from air_quality import (
    KATEGORI_DISPLAY,
    STATIONS,
    FORECAST_HORIZONS,
    predict_forecast,
)

CLI_LABELS = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "so2": "SO2",
    "co": "CO",
    "o3": "O3",
    "no2": "NO2",
}


def main():

    print("\n===== PREDIKSI KUALITAS UDARA DKI JAKARTA (H+1 s/d H+7) =====")
    print("Metode: Direct Forecasting\n")

    # Menyimpan seluruh hasil prediksi
    rows = []

    for horizon in FORECAST_HORIZONS:

        print(f"\n{'=' * 60}")
        print(f"===== HORIZON H+{horizon} =====")
        print(f"{'=' * 60}")

        for stasiun in STATIONS:

            hasil = predict_forecast(stasiun, horizon)

            print(f"\nStasiun               : {stasiun}")
            print(f"Tanggal data terakhir : {hasil['tanggal_terakhir'].date()}")
            print(f"Tanggal prediksi      : {hasil['tanggal_prediksi'].date()}")

            print("\n--- Nilai Polutan ---")

            for key, label in CLI_LABELS.items():

                nilai = hasil["nilai"][key]
                kategori = hasil["kategori_per_polutan"][key]

                print(f"{label:<6}: {nilai:.2f} ({kategori})")

            print(f"\nStatus Kualitas Udara : {KATEGORI_DISPLAY[hasil['status']]}")
            print("-" * 60)

            # Simpan ke list untuk CSV
            rows.append({

                "Horizon": f"H+{horizon}",
                "Stasiun": stasiun,

                "Tanggal Data Terakhir": hasil["tanggal_terakhir"].date(),
                "Tanggal Prediksi": hasil["tanggal_prediksi"].date(),

                "PM2.5": round(hasil["nilai"]["pm25"], 2),
                "Kategori PM2.5": hasil["kategori_per_polutan"]["pm25"],

                "PM10": round(hasil["nilai"]["pm10"], 2),
                "Kategori PM10": hasil["kategori_per_polutan"]["pm10"],

                "SO2": round(hasil["nilai"]["so2"], 2),
                "Kategori SO2": hasil["kategori_per_polutan"]["so2"],

                "CO": round(hasil["nilai"]["co"], 2),
                "Kategori CO": hasil["kategori_per_polutan"]["co"],

                "O3": round(hasil["nilai"]["o3"], 2),
                "Kategori O3": hasil["kategori_per_polutan"]["o3"],

                "NO2": round(hasil["nilai"]["no2"], 2),
                "Kategori NO2": hasil["kategori_per_polutan"]["no2"],

                "Status Kualitas Udara": KATEGORI_DISPLAY[hasil["status"]]

            })

    # ==========================
    # Simpan seluruh hasil ke CSV
    # ==========================

    df = pd.DataFrame(rows)

    nama_file = "hasil_prediksi_7_hari.csv"

    df.to_csv(
        nama_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("SEMUA PREDIKSI BERHASIL DISIMPAN")
    print("=" * 60)
    print(f"Jumlah data : {len(df)}")
    print(f"File CSV    : {nama_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()