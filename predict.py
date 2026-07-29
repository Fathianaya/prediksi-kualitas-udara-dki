"""Skrip CLI prediksi kualitas udara H+1 s/d H+7 DKI Jakarta (Direct Forecasting)."""

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

    for horizon in FORECAST_HORIZONS:
        print(f"\n{'=' * 55}")
        print(f"===== HORIZON H+{horizon} =====")
        print(f"{'=' * 55}")

        for stasiun in STATIONS:
            hasil = predict_forecast(stasiun, horizon)
            print(f"\nStasiun: {stasiun}")
            print(f"Tanggal data terakhir : {hasil['tanggal_terakhir'].date()}")
            print(f"Tanggal prediksi (H+{horizon}): {hasil['tanggal_prediksi'].date()}")
            print("\n--- Nilai Polutan ---")
            for key, label in CLI_LABELS.items():
                kat = hasil["kategori_per_polutan"][key]
                print(f"  {label:6s}: {hasil['nilai'][key]:.2f}  ({kat})")
            print(f"\nStatus kualitas udara: {KATEGORI_DISPLAY[hasil['status']]}")
            print("-" * 50)


if __name__ == "__main__":
    main()
