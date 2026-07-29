import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from air_quality import (
    load_models,
    predict_forecast,
    predict_next_7_days,
    get_forecast_dates,
    horizon_from_date,
    get_last_data_date,
    load_raw_data,
    format_date_id,
    POLLUTANT_LABELS,
    KATEGORI_DISPLAY,
    KATEGORI_COLORS,
    KATEGORI_ORDER,
    STATIONS,
)
from theme import apply_theme

st.set_page_config(page_title="Prediksi 7 Hari", layout="wide")
apply_theme()

st.title("🔮 Prediksi Kualitas Udara DKI Jakarta (7 Hari Ke Depan)")
st.caption(
    "Halaman 2 — Direct forecasting H+1 s/d H+7 menggunakan Random Forest "
    "(model terpisah per horizon)"
)


@st.cache_resource
def get_models(horizon: int):
    """Cache model per horizon agar tidak dimuat ulang setiap interaksi."""
    return load_models(horizon)


@st.cache_data
def _forecast_7_days(stasiun_name: str):
    """Cache prediksi 7 hari per stasiun (direct forecasting)."""
    return predict_next_7_days(stasiun_name)


@st.cache_data
def _forecast_all_stations(horizon: int):
    """Cache prediksi semua stasiun pada horizon tertentu.

    Sebelumnya dihitung ulang setiap kali ada interaksi apa pun di halaman
    (ganti stasiun, ganti tanggal, dll). Dengan cache ini hanya dihitung
    ulang saat horizon-nya benar-benar berubah.
    """
    rows = []
    models = get_models(horizon)
    for s in STATIONS:
        h = predict_forecast(s, horizon, models)
        rows.append({
            "Stasiun": s,
            "Tanggal": h["tanggal_prediksi"].strftime("%Y-%m-%d"),
            "Horizon": f"H+{horizon}",
            "PM2.5": round(h["nilai"]["pm25"], 1),
            "PM10": round(h["nilai"]["pm10"], 1),
            "SO₂": round(h["nilai"]["so2"], 1),
            "CO": round(h["nilai"]["co"], 1),
            "O₃": round(h["nilai"]["o3"], 1),
            "NO₂": round(h["nilai"]["no2"], 1),
            "Status": KATEGORI_DISPLAY.get(h["status"], h["status"]),
        })
    return pd.DataFrame(rows)


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(255,255,255,0.6)",
    plot_bgcolor="rgba(255,255,255,0.6)",
    font=dict(family="DM Sans, sans-serif", color="#1E2E42"),
    title_font=dict(family="Space Grotesk, sans-serif", color="#023E61", size=15),
    margin=dict(t=50, b=40, l=40, r=20),
)

KATEGORI_BG = {
    "BAIK":               "rgba(29,184,116,0.10)",
    "SEDANG":              "rgba(232,160,32,0.10)",
    "TIDAK SEHAT":         "rgba(224,92,64,0.10)",
    "SANGAT TIDAK SEHAT":  "rgba(150,30,200,0.10)",
    "BERBAHAYA":           "rgba(180,0,0,0.10)",
}

# Level alert Streamlit yang paling cocok untuk tiap kategori, urut dari
# ringan ke berat. Dipakai supaya box status & analisis konsisten:
# BAIK -> success, SEDANG -> warning, sisanya -> error.
KATEGORI_ALERT = {
    "BAIK":               "success",
    "SEDANG":              "warning",
    "TIDAK SEHAT":         "error",
    "SANGAT TIDAK SEHAT":  "error",
    "BERBAHAYA":           "error",
}


def show_alert(status: str, message: str):
    """Tampilkan st.success/warning/error sesuai tingkat keparahan kategori."""
    level = KATEGORI_ALERT.get(status, "info")
    getattr(st, level)(message)


# --- Sidebar: stasiun & tanggal prediksi ---
forecast_dates = get_forecast_dates()
last_data_date = get_last_data_date()
date_labels = {format_date_id(d): d for d in forecast_dates}

with st.sidebar:
    st.header("Pengaturan Prediksi")
    stasiun = st.selectbox("Pilih Stasiun", STATIONS)

    st.subheader("Pilih Tanggal Prediksi")
    st.caption(f"Data terakhir: **{format_date_id(last_data_date)}**")
    tanggal_label = st.selectbox(
        "Tanggal prediksi (H+1 s/d H+7)",
        list(date_labels.keys()),
        label_visibility="collapsed",
    )
    tanggal_prediksi = date_labels[tanggal_label]
    horizon = horizon_from_date(tanggal_prediksi)

    st.info(f"Horizon terpilih: **H+{horizon}**")

try:
    models = get_models(horizon)
    hasil = predict_forecast(stasiun, horizon, models)
except Exception as e:
    st.error(f"Gagal memuat prediksi: {e}")
    st.stop()


def _ispu_equivalent(nilai: float, key: str) -> float:
    """CO dikalikan 10 agar konsisten dengan aturan kategori pada sistem."""
    return nilai * 10 if key == "co" else nilai


def _severity_rank(kategori: str) -> int:
    return KATEGORI_ORDER.index(kategori) if kategori in KATEGORI_ORDER else -1


def build_analysis(hasil_prediksi: dict) -> dict:
    rows = []
    for key, label in POLLUTANT_LABELS.items():
        nilai = hasil_prediksi["nilai"][key]
        kategori = hasil_prediksi["kategori_per_polutan"][key]
        rows.append(
            {
                "key": key,
                "label": label,
                "nilai": nilai,
                "kategori": kategori,
                "ispu_equiv": _ispu_equivalent(nilai, key),
                "rank": _severity_rank(kategori),
            }
        )

    rows_sorted = sorted(rows, key=lambda x: (x["rank"], x["ispu_equiv"]), reverse=True)
    dominan = rows_sorted[0]
    status = hasil_prediksi["status"]
    penyebab_utama = [r for r in rows_sorted if r["kategori"] == status]
    if not penyebab_utama:
        penyebab_utama = [dominan]

    return {
        "dominan": dominan,
        "penyebab_utama": penyebab_utama[:2],
        "urutan_risiko": rows_sorted,
    }


analysis = build_analysis(hasil)
dominan = analysis["dominan"]
status = hasil["status"]
label = KATEGORI_DISPLAY.get(status, status)
color = KATEGORI_COLORS.get(status, "#1E9FDB")
bg_status = KATEGORI_BG.get(status, "rgba(30,159,219,0.08)")
horizon_label = f"H+{horizon}"
prediksi_tanggal_str = format_date_id(hasil["tanggal_prediksi"])

# --- Info ringkas (stasiun & judul sudah ada di sidebar/atas, tidak diulang) ---
c1, c2, c3 = st.columns(3)
c1.metric("Data terakhir", format_date_id(hasil["tanggal_terakhir"]))
c2.metric("Horizon", horizon_label)
c3.metric("Tanggal prediksi", prediksi_tanggal_str)

st.divider()

tab_polutan, tab_status, tab_ringkasan, tab_banding = st.tabs(
    [
        "📈 Detail Polutan",
        "🏭 Status & Analisis",
        "📅 Ringkasan 7 Hari",
        "📊 Perbandingan & Semua Stasiun",
    ]
)

# =========================================================
# TAB — DETAIL POLUTAN
# =========================================================
with tab_polutan:
    cols = st.columns(3)
    for idx, (key, nama) in enumerate(POLLUTANT_LABELS.items()):
        nilai = hasil["nilai"][key]
        kat = hasil["kategori_per_polutan"][key]
        with cols[idx % 3]:
            st.metric(
                nama,
                f"{nilai:.2f}",
                delta=KATEGORI_DISPLAY.get(kat, kat),
                delta_color="off",
            )

    fig = go.Figure(
        go.Bar(
            x=[POLLUTANT_LABELS[k] for k in hasil["nilai"]],
            y=list(hasil["nilai"].values()),
            marker_color=[
                KATEGORI_COLORS.get(hasil["kategori_per_polutan"][k], "#1E9FDB")
                for k in hasil["nilai"]
            ],
            marker_line_color="rgba(255,255,255,0.6)",
            marker_line_width=1.5,
            text=[f"{v:.1f}" for v in hasil["nilai"].values()],
            textposition="outside",
            textfont=dict(family="Space Grotesk, sans-serif", color="#023E61", size=12),
        )
    )
    fig.update_layout(
        title=f"Prediksi Konsentrasi Polutan — {stasiun} ({horizon_label})",
        yaxis_title="Nilai",
        height=400,
        yaxis=dict(showgrid=True, gridcolor="#EFF3F8", gridwidth=1),
        xaxis=dict(showgrid=False),
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig, use_container_width=True)

    detail = pd.DataFrame(
        {
            "Polutan": [POLLUTANT_LABELS[k] for k in hasil["nilai"]],
            f"Prediksi {horizon_label}": [round(hasil["nilai"][k], 2) for k in hasil["nilai"]],
            "Kategori": [
                KATEGORI_DISPLAY.get(hasil["kategori_per_polutan"][k], hasil["kategori_per_polutan"][k])
                for k in hasil["nilai"]
            ],
        }
    )
    st.dataframe(detail, use_container_width=True, hide_index=True)

# =========================================================
# TAB — STATUS & ANALISIS
# =========================================================
with tab_status:
    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:28px 24px;
            border-radius:14px;
            background:{bg_status};
            border:2px solid {color};
            box-shadow:0 4px 16px rgba(0,0,0,0.06);
            backdrop-filter:blur(6px);
        ">
            <div style="
                font-family:'Space Grotesk',sans-serif;
                font-size:2.4em;
                font-weight:700;
                color:{color};
                letter-spacing:-0.02em;
            ">{label}</div>
            <div style="
                font-size:0.88rem;
                color:#5B6E88;
                margin-top:6px;
                font-family:'DM Sans',sans-serif;
            ">Prediksi {horizon_label} · {prediksi_tanggal_str} · {stasiun}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("📋 Skala Kategori ISPU (referensi)"):
        ref = pd.DataFrame(
            {
                "Kategori": [KATEGORI_DISPLAY[k] for k in KATEGORI_ORDER],
                "Rentang Indeks": ["0 – 50", "51 – 100", "101 – 200", "201 – 300", "> 300"],
            }
        )
        st.table(ref)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # Satu blok naratif gabungan (status + polutan dominan), levelnya
    # otomatis mengikuti keparahan kategori lewat show_alert().
    if status == "BAIK":
        pesan = f"""
Kualitas udara di **{stasiun}** pada tanggal **{prediksi_tanggal_str}** ({horizon_label})
diprediksi berada pada kategori **{label}**.

Polutan dengan nilai tertinggi adalah **{dominan['label']}** sebesar **{dominan['nilai']:.2f}**,
namun masih berada pada tingkat yang aman.
"""
    else:
        pesan = f"""
Kualitas udara di **{stasiun}** pada tanggal **{prediksi_tanggal_str}** ({horizon_label})
diprediksi berada pada kategori **{label}**.

Polutan dominan penyebab kondisi tersebut adalah **{dominan['label']}**
dengan nilai prediksi **{dominan['nilai']:.2f}** — termasuk kategori
**{KATEGORI_DISPLAY.get(dominan['kategori'], dominan['kategori'])}**.
"""
        if status in ("TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"):
            pesan += "\nDisarankan untuk mengurangi aktivitas di luar ruangan."
        elif status == "SEDANG":
            pesan += "\nTetap waspada bagi kelompok sensitif."

    show_alert(status, pesan)

    if dominan["key"] == "co":
        st.caption("Catatan: nilai CO dikonversi ke nilai setara ISPU dengan faktor ×10.")

# =========================================================
# TAB — RINGKASAN 7 HARI
# =========================================================
with tab_ringkasan:
    st.caption(
        f"Proyeksi direct forecasting untuk **{stasiun}** — "
        "setiap baris memakai model horizon terpisah (bukan prediksi berantai)."
    )

    forecast_week = _forecast_7_days(stasiun)
    overview_rows = [
        {
            "Horizon": f"H+{day['horizon']}",
            "Tanggal": format_date_id(day["tanggal"]),
            "PM2.5": round(day["nilai"]["pm25"], 1),
            "PM10": round(day["nilai"]["pm10"], 1),
            "Status": KATEGORI_DISPLAY.get(day["kategori"], day["kategori"]),
        }
        for day in forecast_week
    ]
    overview_df = pd.DataFrame(overview_rows)

    fig_week = go.Figure()
    fig_week.add_trace(
        go.Scatter(
            x=overview_df["Tanggal"],
            y=overview_df["PM2.5"],
            mode="lines+markers",
            name="PM2.5",
            line=dict(color="#E05C40", width=2.5),
            marker=dict(size=9),
        )
    )
    selected_idx = horizon - 1
    fig_week.add_trace(
        go.Scatter(
            x=[overview_df["Tanggal"].iloc[selected_idx]],
            y=[overview_df["PM2.5"].iloc[selected_idx]],
            mode="markers",
            name=f"Terpilih ({horizon_label})",
            marker=dict(size=14, color="#023E61", symbol="circle-open", line=dict(width=3)),
        )
    )
    fig_week.update_layout(
        title=f"Tren PM2.5 — {stasiun}",
        yaxis_title="PM2.5 (µg/m³)",
        height=320,
        showlegend=True,
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig_week, use_container_width=True)
    st.dataframe(overview_df, use_container_width=True, hide_index=True)

# =========================================================
# TAB — PERBANDINGAN & SEMUA STASIUN
# =========================================================
with tab_banding:
    st.subheader(f"Hari Ini vs Prediksi {horizon_label}")

    raw = load_raw_data()
    data_hari_ini = (
        raw[raw["stasiun"] == stasiun]
        .sort_values("tanggal_lengkap")
        .tail(1)
    )

    aktual = {
        "PM2.5": float(data_hari_ini["pm_duakomalima"].iloc[0]),
        "PM10": float(data_hari_ini["pm_sepuluh"].iloc[0]),
        "SO₂": float(data_hari_ini["sulfur_dioksida"].iloc[0]),
        "CO": float(data_hari_ini["karbon_monoksida"].iloc[0]),
        "O₃": float(data_hari_ini["ozon"].iloc[0]),
        "NO₂": float(data_hari_ini["nitrogen_dioksida"].iloc[0]),
    }
    prediksi = {
        "PM2.5": hasil["nilai"]["pm25"],
        "PM10": hasil["nilai"]["pm10"],
        "SO₂": hasil["nilai"]["so2"],
        "CO": hasil["nilai"]["co"],
        "O₃": hasil["nilai"]["o3"],
        "NO₂": hasil["nilai"]["no2"],
    }
    pred_col = f"Prediksi {horizon_label}"
    compare_df = pd.DataFrame({
        "Polutan": list(aktual.keys()),
        "Hari Ini": list(aktual.values()),
        pred_col: list(prediksi.values()),
    })

    fig_compare = go.Figure()
    fig_compare.add_bar(name="Hari Ini", x=compare_df["Polutan"], y=compare_df["Hari Ini"])
    fig_compare.add_bar(name=pred_col, x=compare_df["Polutan"], y=compare_df[pred_col])
    fig_compare.update_layout(
        barmode="group",
        title=f"Perbandingan Konsentrasi Polutan ({stasiun})",
        height=450,
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    selisih_pm25 = hasil["nilai"]["pm25"] - aktual["PM2.5"]
    arah = "meningkat" if selisih_pm25 > 0 else "menurun"

    st.info(
        f"""
📌 Insight

• Grafik membandingkan kondisi aktual hari terakhir dengan prediksi **{horizon_label}** ({prediksi_tanggal_str}).

• PM2.5 diprediksi **{arah}** sebesar **{abs(selisih_pm25):.2f}** poin dibanding hari ini.

• Model **H+{horizon}** dipakai langsung (direct forecasting), tanpa prediksi berantai.
"""
    )

    st.divider()

    st.subheader(f"Ringkasan Semua Stasiun ({horizon_label})")
    all_stations_df = _forecast_all_stations(horizon)
    st.dataframe(all_stations_df, use_container_width=True, hide_index=True)

    severity = {
        "Baik": 1,
        "Sedang (Cukup Sehat)": 2,
        "Tidak Sehat": 3,
        "Sangat Tidak Sehat": 4,
        "Berbahaya": 5,
    }
    ranking_df = all_stations_df.copy()
    ranking_df["Severity"] = ranking_df["Status"].map(severity)
    terburuk = ranking_df.sort_values(by=["Severity", "PM2.5"], ascending=False).iloc[0]

    # Cari key kategori (bukan label tampilan) dari status stasiun terburuk,
    # supaya warna alert konsisten dengan tingkat keparahannya sendiri —
    # bukan mengikuti status stasiun yang sedang dipilih di sidebar.
    _label_to_key = {v: k for k, v in KATEGORI_DISPLAY.items()}
    status_terburuk = _label_to_key.get(terburuk["Status"], terburuk["Status"])

    st.subheader("🚨 Analisis Risiko Antar Stasiun")
    show_alert(
        status_terburuk,
        f"""
Berdasarkan prediksi **{horizon_label}** ({prediksi_tanggal_str}), **{terburuk['Stasiun']}**
diperkirakan memiliki tingkat risiko pencemaran udara tertinggi dibanding stasiun lainnya.

Status kualitas udara: **{terburuk['Status']}** pada tanggal prediksi terpilih.
""",
    )

st.divider()
st.caption(
    "Model: Random Forest (500 estimators) | Direct forecasting H+1–H+7 | "
    "Fitur: lag 1/2/3/7/14/30 hari + fitur waktu + stasiun"
)