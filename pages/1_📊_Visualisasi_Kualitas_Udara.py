import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from air_quality import (
    load_raw_data,
    ringkasan_stasiun_terkini,
    KATEGORI_COLORS,
    KATEGORI_DISPLAY,
    STATIONS,
)

from theme import apply_theme


st.set_page_config(
    page_title="Visualisasi ISPU",
    layout="wide"
)

apply_theme()

st.title("📊 Visualisasi Kualitas Udara DKI Jakarta")

st.caption(
    "Halaman 1 — Monitoring historis kualitas udara per stasiun"
)

# =====================================================
# HELPER: kategori ISPU & penjelasan sumber polutan
# =====================================================

def kategori_ispu(nilai: float) -> str:
    """Mengembalikan label kategori ISPU sesuai rentang standar."""
    if nilai <= 50:
        return "Baik"
    elif nilai <= 100:
        return "Sedang"
    elif nilai <= 199:
        return "Tidak Sehat"
    elif nilai <= 299:
        return "Sangat Tidak Sehat"
    else:
        return "Berbahaya"


# Urutan kategori standar ISPU, dipakai untuk legend & pemetaan warna
URUTAN_KATEGORI = ["Baik", "Sedang", "Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"]

# Fallback warna kalau KATEGORI_COLORS dari air_quality.py tidak lengkap
_FALLBACK_COLORS = {
    "Baik": "#00A651",
    "Sedang": "#FFD700",
    "Tidak Sehat": "#FF8C00",
    "Sangat Tidak Sehat": "#E53935",
    "Berbahaya": "#7B0000",
}

def warna_kategori(kategori: str) -> str:
    try:
        return KATEGORI_COLORS.get(kategori, _FALLBACK_COLORS.get(kategori, "#999999"))
    except Exception:
        return _FALLBACK_COLORS.get(kategori, "#999999")

def label_kategori(kategori: str) -> str:
    try:
        return KATEGORI_DISPLAY.get(kategori, kategori)
    except Exception:
        return kategori

# =====================================================
# LOAD DATA
# =====================================================
df = load_raw_data()

min_date = df["tanggal_lengkap"].min().date()
max_date = df["tanggal_lengkap"].max().date()

# =====================================================
# FILTER
# =====================================================
with st.sidebar:

    st.subheader("Stasiun")

    # Pilih semua / hapus semua, tanpa mengubah default (semua tercentang)
    col_a, col_b = st.columns(2)
    if col_a.button("Pilih Semua", use_container_width=True):
        for s in STATIONS:
            st.session_state[f"stasiun_{s}"] = True
    if col_b.button("Hapus Semua", use_container_width=True):
        for s in STATIONS:
            st.session_state[f"stasiun_{s}"] = False

    stasiun_filter = []

    for s in STATIONS:

        if st.checkbox(
            s,
            value=True,
            key=f"stasiun_{s}"
        ):
            stasiun_filter.append(s)

    st.subheader("Periode Data")
    tgl_mulai = st.date_input(
        "Tanggal mulai",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY"
    )
    tgl_akhir = st.date_input(
        "Tanggal akhir",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        format="DD/MM/YYYY"

    )

    if tgl_mulai > tgl_akhir:


        st.warning(
            "Tanggal mulai tidak boleh lebih besar dari tanggal akhir"
        )


        st.stop()

mask = (

    df["stasiun"].isin(stasiun_filter)

    &

    (df["tanggal_lengkap"].dt.date >= tgl_mulai)

    &

    (df["tanggal_lengkap"].dt.date <= tgl_akhir)
)

filtered = df.loc[mask].copy()

if filtered.empty:
    st.warning(
        "Tidak ada data berdasarkan filter"
    )


    st.stop()

# =====================================================
# METRIK
# =====================================================
m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Total Observasi",
    f"{len(filtered):,}"
)

m2.metric(
    "Rata-rata PM2.5",
    f"{filtered['pm_duakomalima'].mean():.1f}"
)

m3.metric(
    "Rata-rata PM10",
    f"{filtered['pm_sepuluh'].mean():.1f}"
)

m4.metric(
    "Rata-rata ISPU",
    f"{filtered['max'].mean():.1f}"
)

# Badge kategori ISPU keseluruhan periode terpilih
kategori_periode = kategori_ispu(filtered["max"].mean())
st.markdown(
    f"""
    <div style="
        display:inline-block;
        padding:6px 16px;
        border-radius:20px;
        background:{warna_kategori(kategori_periode)}22;
        border:1px solid {warna_kategori(kategori_periode)};
        color:{warna_kategori(kategori_periode)};
        font-weight:600;
        margin-top:8px;
        margin-bottom:8px;
    ">
        ● Kondisi rata-rata periode ini: {label_kategori(kategori_periode)}
    </div>
    """,
    unsafe_allow_html=True,
)


PLOTLY_LAYOUT = dict(

paper_bgcolor="rgba(255,255,255,0.6)",

plot_bgcolor="rgba(255,255,255,0.6)",

margin=dict(
t=50,
b=40,
l=40,
r=20
)
)

tab_heatmap, tab_ranking, tab_polutan, tab_tren, tab_data = st.tabs(
    ["🗓️ Heatmap PM2.5", "🏆 Ranking ISPU", "🧪 Polutan", "📈 Tren ISPU", "📋 Data"]
)

# =====================================================
# 1 HEATMAP PM2.5
# =====================================================
with tab_heatmap:
    st.subheader(
        "Heatmap Rata-rata PM2.5 per Bulan dan Stasiun"
    )

    heatmap = filtered.copy()

    heatmap["bulan"] = (

        heatmap["tanggal_lengkap"]
        .dt.strftime("%b")

    )

    pivot = heatmap.pivot_table(
    values="pm_duakomalima",
    index="stasiun",
    columns="bulan",
    aggfunc="mean"
    )

    fig = px.imshow(
    pivot,
    text_auto=".1f",
    color_continuous_scale="YlOrRd",
    title="Distribusi PM2.5"
    )

    fig.update_layout(
    height=450,
    **PLOTLY_LAYOUT
    )

    st.plotly_chart(

    fig,

    use_container_width=True

    )


    # =====================================================
    # INSIGHT DINAMIS HEATMAP
    # =====================================================

    tanggal_awal = filtered["tanggal_lengkap"].min().strftime("%d %B %Y")
    tanggal_akhir = filtered["tanggal_lengkap"].max().strftime("%d %B %Y")

    # nilai tertinggi
    max_pm25 = filtered.loc[
        filtered["pm_duakomalima"].idxmax()
    ]

    # nilai terendah
    min_pm25 = filtered.loc[
        filtered["pm_duakomalima"].idxmin()
    ]

    overall_mean = filtered["pm_duakomalima"].mean()

    selisih = (
        max_pm25["pm_duakomalima"] -
        min_pm25["pm_duakomalima"]
    )

    st.info(f"""
### 📌 Insight Periode Terpilih

Berdasarkan data **{tanggal_awal}** hingga **{tanggal_akhir}**, rata-rata PM2.5 seluruh stasiun adalah **{overall_mean:.2f} μg/m³**.

Nilai PM2.5 tertinggi terjadi di **{max_pm25['stasiun']}** pada **{max_pm25['tanggal_lengkap'].strftime('%d %B %Y')}** sebesar **{max_pm25['pm_duakomalima']:.2f} μg/m³**.

Sedangkan nilai terendah tercatat di **{min_pm25['stasiun']}** pada **{min_pm25['tanggal_lengkap'].strftime('%d %B %Y')}** sebesar **{min_pm25['pm_duakomalima']:.2f} μg/m³**.

Selisih antara nilai maksimum dan minimum selama periode ini adalah **{selisih:.2f} μg/m³**.
""")

# =====================================================
# 2 RANKING ISPU
# =====================================================
with tab_ranking:

    st.subheader(
    "Ranking Stasiun Berdasarkan ISPU"
    )

    ranking = (

    filtered.groupby("stasiun")["max"]

    .mean()

    .sort_values()

    .reset_index()

    )

    # Kategori per stasiun, dipetakan ke warna resmi ISPU
    ranking["kategori"] = ranking["max"].apply(kategori_ispu)

    fig = px.bar(

    ranking,

    x="max",

    y="stasiun",

    orientation="h",

    text="max",

    color="kategori",

    category_orders={"kategori": URUTAN_KATEGORI},

    color_discrete_map={k: warna_kategori(k) for k in URUTAN_KATEGORI},

    title="Rata-rata ISPU per Stasiun"

    )



    fig.update_traces(

    texttemplate="%{text:.1f}"

    )



    fig.update_layout(

    height=450,

    legend_title_text="Kategori",

    **PLOTLY_LAYOUT

    )



    st.plotly_chart(

    fig,

    use_container_width=True

    )


    # =====================================================
    # INSIGHT DINAMIS RANKING ISPU
    # =====================================================

    terbaik = ranking.iloc[0]
    terburuk = ranking.iloc[-1]

    selisih = terburuk["max"] - terbaik["max"]

    st.info(f"""
### 📌 Insight Periode Terpilih

Pada periode **{tanggal_awal}** hingga **{tanggal_akhir}**, stasiun dengan rata-rata ISPU tertinggi adalah **{terburuk['stasiun']}** dengan nilai **{terburuk['max']:.2f}**.

Sedangkan stasiun dengan rata-rata ISPU terendah adalah **{terbaik['stasiun']}** dengan nilai **{terbaik['max']:.2f}**.

Perbedaan rata-rata ISPU antar kedua stasiun mencapai **{selisih:.2f} poin**.
""")

# =====================================================
# 3 POLUTAN
# =====================================================
with tab_polutan:

    st.subheader(
    "Rata-rata Konsentrasi Polutan"
    )

    polutan = pd.DataFrame({

    "Polutan":[

    "PM2.5",

    "PM10",

    "SO2",

    "CO",

    "O3",

    "NO2"

    ],

    "Rata-rata":[

    filtered["pm_duakomalima"].mean(),

    filtered["pm_sepuluh"].mean(),

    filtered["sulfur_dioksida"].mean(),

    filtered["karbon_monoksida"].mean(),

    filtered["ozon"].mean(),

    filtered["nitrogen_dioksida"].mean()

    ]

    })



    fig = px.bar(
        polutan,
        x="Polutan",
        y="Rata-rata",
        color="Polutan",
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="Rata-rata Konsentrasi Polutan"
    )

    fig.update_traces(showlegend=False)  # opsional: warna sudah jelas dari sumbu X, legend jadi redundan


    fig.update_layout(

    height=450,

    **PLOTLY_LAYOUT

    )

    st.plotly_chart(

    fig,

    use_container_width=True

    )


    # =====================================================
    # INSIGHT DINAMIS POLUTAN
    # =====================================================
    dominan = polutan.sort_values(
        "Rata-rata",
        ascending=False
    ).iloc[0]

    kontribusi = (
        dominan["Rata-rata"] /
        polutan["Rata-rata"].sum()
    ) * 100

    kolom_polutan = {
        "PM2.5": "pm_duakomalima",
        "PM10": "pm_sepuluh",
        "SO2": "sulfur_dioksida",
        "CO": "karbon_monoksida",
        "O3": "ozon",
        "NO2": "nitrogen_dioksida"
    }

    kolom = kolom_polutan[dominan["Polutan"]]

    tertinggi = filtered.loc[
        filtered[kolom].idxmax()
    ]

    terendah = filtered.loc[
        filtered[kolom].idxmin()
    ]

    st.info(f"""
### 📌 Insight Periode Terpilih

Selama periode **{tanggal_awal}** hingga **{tanggal_akhir}**, polutan yang memiliki rata-rata konsentrasi tertinggi adalah **{dominan['Polutan']}** dengan nilai **{dominan['Rata-rata']:.2f}**.

Nilai tersebut menyumbang sekitar **{kontribusi:.1f}%** dari total rata-rata seluruh polutan yang diamati.

Konsentrasi tertinggi **{dominan['Polutan']}** terjadi pada **{tertinggi['tanggal_lengkap'].strftime('%d %B %Y')}** di **{tertinggi['stasiun']}** sebesar **{tertinggi[kolom]:.2f}**.

Sedangkan konsentrasi terendah tercatat pada **{terendah['tanggal_lengkap'].strftime('%d %B %Y')}** di **{terendah['stasiun']}** sebesar **{terendah[kolom]:.2f}**.
""")

# =====================================================
# 4 TREND ISPU
# =====================================================
with tab_tren:

    st.subheader(
    "Tren Indeks ISPU"
    )

    tren = filtered.groupby(
        ["tanggal_lengkap", "stasiun"]
    )["max"].mean().reset_index()

    # Rata-rata bergerak 14 hari agar garis lebih halus dan mudah dibaca
    tren = tren.sort_values(["stasiun", "tanggal_lengkap"])
    tren["ma14"] = (
        tren.groupby("stasiun")["max"]
        .transform(lambda s: s.rolling(14, min_periods=1).mean())
    )

    fig = px.line(
        tren,
        x="tanggal_lengkap",
        y="ma14",
        color="stasiun",
        color_discrete_sequence=px.colors.qualitative.Set2,
        title="Tren ISPU per Stasiun (Rata-rata Bergerak 14 Hari)"
    )

    fig.update_traces(line_width=2)

    fig.update_layout(
        height=500,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        ),
        xaxis=dict(
            rangeslider=dict(visible=True),  # slider zoom di bawah chart
            type="date"
        ),
        **PLOTLY_LAYOUT
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "📌 Garis menunjukkan rata-rata bergerak 14 hari. Gunakan slider di bawah chart "
        "untuk memperbesar (zoom) periode tertentu."
    )



    # =====================================================
    # INSIGHT DINAMIS TREN ISPU
    # =====================================================

    # rata-rata harian seluruh stasiun
    tren_harian = (
        filtered.groupby("tanggal_lengkap")["max"]
        .mean()
        .reset_index()
    )

    # ============================
    # arah tren
    # ============================

    if len(tren_harian) > 1:
        slope = np.polyfit(
            range(len(tren_harian)),
            tren_harian["max"],
            1
        )[0]
    else:
        slope = 0

    if slope > 0.05:
        arah = "meningkat"
    elif slope < -0.05:
        arah = "menurun"
    else:
        arah = "relatif stabil"

    # ============================
    # awal vs akhir periode
    # ============================

    awal = tren_harian.iloc[0]["max"]
    akhir = tren_harian.iloc[-1]["max"]

    perubahan = akhir - awal

    if awal != 0:
        perubahan_pct = (perubahan / awal) * 100
    else:
        perubahan_pct = 0

    # ============================
    # nilai maksimum
    # ============================

    puncak = filtered.loc[
        filtered["max"].idxmax()
    ]

    # ============================
    # nilai minimum
    # ============================

    terendah = filtered.loc[
        filtered["max"].idxmin()
    ]

    # ============================
    # stasiun rata-rata tertinggi
    # ============================

    ranking_ispu = (
        filtered.groupby("stasiun")["max"]
        .mean()
        .sort_values(ascending=False)
    )

    stasiun_terburuk = ranking_ispu.index[0]
    nilai_terburuk = ranking_ispu.iloc[0]

    stasiun_terbaik = ranking_ispu.index[-1]
    nilai_terbaik = ranking_ispu.iloc[-1]

    # ============================
    # fluktuasi terbesar
    # ============================

    fluktuasi = (
        filtered.groupby("stasiun")["max"]
        .std()
        .sort_values(ascending=False)
    )

    stasiun_fluktuatif = fluktuasi.index[0]
    std_fluktuasi = fluktuasi.iloc[0]

    # =====================================================
    # TAMPILKAN INSIGHT
    # =====================================================

    st.info(f"""
### 📌 Insight Periode Terpilih

Periode analisis yang digunakan adalah **{tanggal_awal}** hingga **{tanggal_akhir}**.

Selama periode tersebut, rata-rata ISPU menunjukkan tren **{arah}**.

Nilai rata-rata ISPU berubah dari **{awal:.2f}** pada awal periode menjadi **{akhir:.2f}** pada akhir periode (**{perubahan_pct:+.1f}%**).

Nilai ISPU tertinggi tercatat pada **{puncak['tanggal_lengkap'].strftime('%d %B %Y')}** di **{puncak['stasiun']}** sebesar **{puncak['max']:.2f}**.

Nilai ISPU terendah tercatat pada **{terendah['tanggal_lengkap'].strftime('%d %B %Y')}** di **{terendah['stasiun']}** sebesar **{terendah['max']:.2f}**.

Berdasarkan rata-rata selama periode ini, **{stasiun_terburuk}** memiliki ISPU tertinggi (**{nilai_terburuk:.2f}**), sedangkan **{stasiun_terbaik}** memiliki rata-rata terendah (**{nilai_terbaik:.2f}**).

Stasiun dengan fluktuasi ISPU terbesar adalah **{stasiun_fluktuatif}** dengan simpangan baku **{std_fluktuasi:.2f}**, yang menunjukkan perubahan kualitas udara paling dinamis dibanding stasiun lainnya.
""")

with tab_data:
    st.subheader(
    "Data Terfilter"
    )

    tabel_tampil = filtered.copy()
    tabel_tampil["Kategori ISPU"] = tabel_tampil["max"].apply(kategori_ispu)

    st.download_button(
        "⬇️ Unduh data terfilter (CSV)",
        data=tabel_tampil.to_csv(index=False).encode("utf-8"),
        file_name=f"ispu_terfilter_{tgl_mulai}_{tgl_akhir}.csv",
        mime="text/csv",
    )

    st.dataframe(
    tabel_tampil,
    use_container_width=True,
    hide_index=True

    )