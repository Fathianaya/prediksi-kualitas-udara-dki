import pandas as pd

# =========================================================
# MEMBACA DATASET
# =========================================================

df = pd.read_csv(
    'datasets/Filedata Data Indeks Standar Pencemar Udara ISPU di Provinsi DKI Jakarta.csv'
)

# =========================================================
# MEMBERSIHKAN NAMA STASIUN
# =========================================================

df['stasiun'] = df['stasiun'].replace({

    # DKI1
    'DKI1  Bundaran Hotel Indonesia (HI)': 'DKI1 Bundaran HI',
    'DKI1 Bundaran Hotel Indonesia (HI)': 'DKI1 Bundaran HI',
    'DKI1 Bundaran Hotel Indonesia  HI': 'DKI1 Bundaran HI',
    'DKI1  Bunderan HI': 'DKI1 Bundaran HI',

    # DKI2
    'DKI2  Kelapa Gading': 'DKI2 Kelapa Gading',

    # DKI3
    'DKI3  Jagakarsa': 'DKI3 Jagakarsa',

    # DKI4
    'DKI4  Lubang Buaya': 'DKI4 Lubang Buaya',

    # DKI5
    'DKI5  Kebon Jeruk  Jakarta Barat': 'DKI5 Kebon Jeruk',
    'DKI5 Kebon Jeruk Jakarta Barat': 'DKI5 Kebon Jeruk'
})

# =========================================================
# MEMBUAT TANGGAL LENGKAP
# =========================================================

df['tahun'] = df['periode_data'].astype(str).str[:4]

df['tanggal_lengkap'] = pd.to_datetime(
    df['tahun'] + '-' +
    df['bulan'].astype(str) + '-' +
    df['tanggal'].astype(str),
    errors='coerce'
)

# =========================================================
# CEK DATA TANGGAL ERROR
# =========================================================

print("\n===== DATA TANGGAL ERROR =====")

print(
    df[df['tanggal_lengkap'].isnull()][
        ['periode_data', 'bulan', 'tanggal', 'stasiun']
    ]
)

# =========================================================
# HAPUS TANGGAL TIDAK VALID
# =========================================================

df = df.dropna(subset=['tanggal_lengkap'])

print("\nJumlah data setelah hapus tanggal error:")
print(len(df))

# =========================================================
# URUTKAN BERDASARKAN STASIUN DAN TANGGAL
# =========================================================

df = df.sort_values(
    by=['stasiun', 'tanggal_lengkap']
)

# =========================================================
# CEK TANGGAL HILANG PER STASIUN
# =========================================================

for stasiun in df['stasiun'].unique():

    data_stasiun = df[df['stasiun'] == stasiun]

    tanggal_lengkap = pd.date_range(
        start=data_stasiun['tanggal_lengkap'].min(),
        end=data_stasiun['tanggal_lengkap'].max(),
        freq='D'
    )

    tanggal_hilang = tanggal_lengkap.difference(
        data_stasiun['tanggal_lengkap']
    )

    print(f"\n{stasiun}")
    print(f"Jumlah tanggal hilang: {len(tanggal_hilang)}")

# =========================================================
# CEK MISSING VALUE SEBELUM INTERPOLASI
# =========================================================

print("\n===== MISSING VALUE SEBELUM =====")
print(df.isnull().sum())

# =========================================================
# INTERPOLASI DATA NUMERIK
# =========================================================

kolom_numerik = [
    'pm_sepuluh',
    'pm_duakomalima',
    'sulfur_dioksida',
    'karbon_monoksida',
    'ozon',
    'nitrogen_dioksida',
    'max'
]

for kolom in kolom_numerik:
    df[kolom] = (
        df.groupby('stasiun')[kolom]
        .transform(lambda x: x.interpolate(method='linear'))
    )

# =========================================================
# ISI NILAI AWAL / AKHIR YANG MASIH KOSONG
# =========================================================

for kolom in kolom_numerik:
    df[kolom] = (
        df.groupby('stasiun')[kolom]
        .transform(lambda x: x.bfill().ffill())
    )

# =========================================================
# ISI DATA KATEGORI YANG KOSONG
# =========================================================

df['kategori'] = df['kategori'].fillna('SEDANG')
df['parameter_pencemar_kritis'] = (
    df['parameter_pencemar_kritis']
    .fillna('PM25')
)

# =========================================================
# CEK MISSING VALUE SETELAH INTERPOLASI
# =========================================================

print("\n===== MISSING VALUE SETELAH =====")
print(df.isnull().sum())

# =========================================================
# SIMPAN DATA BERSIH
# =========================================================

df.to_csv(
    'datasets/data_ispu_clean.csv',
    index=False
)

print("\nDataset bersih berhasil disimpan")
print("datasets/data_ispu_clean.csv")