import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

from air_quality import (
    load_raw_data,
    ringkasan_stasiun_terkini,
    KATEGORI_COLORS,
    KATEGORI_DISPLAY,
    KATEGORI_ORDER,
    format_date_id,
)
from theme import apply_theme

st.set_page_config(
    page_title="Kualitas Udara DKI Jakarta",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Styling terpusat di theme.py — supaya semua halaman (Ringkasan, Visualisasi,
# Prediksi) selalu konsisten dan cukup diubah dari satu tempat.
apply_theme()

# ── Helper: hapus indentasi awal tiap baris pada HTML ──
# st.markdown() menafsirkan baris yang diawali 4+ spasi sebagai code block
# (aturan Markdown standar). Karena HTML kita ditulis dengan indentasi rapi
# mengikuti gaya kode Python, itu bisa membuat tag-tag HTML tampil sebagai
# teks mentah alih-alih dirender. Fungsi ini menghapus indentasi tersebut
# sebelum HTML dikirim ke st.markdown().
import re


def _flatten_html(html: str) -> str:
    return re.sub(r"^[ \t]+", "", html, flags=re.MULTILINE).strip()


# ── Card helper — dipakai berulang untuk KPI, polutan, status stasiun, info ──
def card(content_html: str, accent: str, height: str = "auto", radius: str = "14px") -> str:
    """Bungkus konten HTML dalam kartu putih dengan aksen warna di atas.

    `height` dipakai sebagai min-height (bukan height tetap) supaya kartu
    bisa memanjang mengikuti isi konten yang lebih panjang dari perkiraan,
    alih-alih kontennya meluber dan menempel ke elemen di bawahnya.
    """
    html = f"""
    <div style="background:#ffffff;border:0.5px solid rgba(0,0,0,0.08);
                border-radius:{radius};padding:1.1rem 1.2rem;position:relative;
                overflow:hidden;box-shadow:0 2px 10px rgba(10,111,163,0.06);
                min-height:{height};margin-bottom:1rem;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:{accent};border-radius:{radius} {radius} 0 0;"></div>
        {content_html}
    </div>
    """
    return _flatten_html(html)


st.title("🌫️ Sistem Kualitas Udara DKI Jakarta")

# ─────────────────────────────────────────────
# LOAD DATA (dengan penanganan error)
# ─────────────────────────────────────────────
try:
    df_home = load_raw_data()
    ringkasan_home = ringkasan_stasiun_terkini(df_home)
except Exception as e:
    st.error(f"Gagal memuat data kualitas udara: {e}")
    st.stop()

# Kolom nilai ISPU yang dipakai konsisten di seluruh halaman (dulu ditulis
# ulang 3x terpisah untuk rata-rata, stasiun terburuk, dan terbaik).
ispu_col = "ispu" if "ispu" in ringkasan_home.columns else "max"

tanggal_awal = format_date_id(df_home["tanggal_lengkap"].min())
tanggal_terkini = format_date_id(df_home["tanggal_lengkap"].max())

st.caption(
    f"Memantau **{len(ringkasan_home)} stasiun** di seluruh DKI Jakarta untuk "
    f"**6 parameter polutan**. Dataset mencakup periode **{tanggal_awal}** s/d "
    f"**{tanggal_terkini}** · 🕒 Data terakhir diperbarui **{tanggal_terkini}**."
)

# ─────────────────────────────────────────────
# RINGKASAN EKSEKUTIF
# ─────────────────────────────────────────────
st.markdown("## 📋 Ringkasan Eksekutif")

# ── KPI utama ──
rata_ispu = ringkasan_home[ispu_col].mean()
stasiun_terburuk = ringkasan_home.loc[ringkasan_home[ispu_col].idxmax()]
stasiun_terbaik = ringkasan_home.loc[ringkasan_home[ispu_col].idxmin()]
kategori_dominan = ringkasan_home["kategori"].mode()[0] if not ringkasan_home["kategori"].mode().empty else "-"

k1, k2, k3, k4 = st.columns(4)

kpi_data = [
    (k1, f"Rata-rata ISPU per {tanggal_terkini}", f"{rata_ispu:.0f}", "#1E9FDB", "📊"),
    (k2, "Kategori Dominan", KATEGORI_DISPLAY.get(kategori_dominan, kategori_dominan), "#E8A020", "🏷️"),
    (k3, "Stasiun Paling Tercemar", stasiun_terburuk["stasiun"].split(" ", 1)[0], "#E05C40", "⚠️"),
    (k4, "Stasiun Paling Bersih", stasiun_terbaik["stasiun"].split(" ", 1)[0], "#1DB874", "✅"),
]

for col, label, value, accent, icon in kpi_data:
    with col:
        font_size = "1.6rem" if len(str(value)) <= 8 else "1.15rem"
        content = f"""
            <p style="font-size:11px;color:#9AAAC0;margin:8px 0 6px;
                      text-transform:uppercase;letter-spacing:0.05em;">
                {icon} {label}
            </p>
            <p style="font-size:{font_size};font-weight:700;color:#1E2E42;
                      margin:0;line-height:1.3;word-wrap:break-word;">
                {value}
            </p>
        """
        st.markdown(card(content, accent, height="100%"), unsafe_allow_html=True)

with st.expander("📋 Apa arti kategori ISPU ini?"):
    ref = pd.DataFrame(
        {
            "Kategori": [KATEGORI_DISPLAY[k] for k in KATEGORI_ORDER],
            "Rentang Indeks": ["0 – 50", "51 – 100", "101 – 200", "201 – 300", "> 300"],
        }
    )
    st.table(ref)

BADGE_STYLE = {
    "BAIK":               ("#EAF3DE", "#27500A", "#3B6D11"),
    "SEDANG":             ("#FAEEDA", "#633806", "#BA7517"),
    "TIDAK SEHAT":        ("#FCEBEB", "#791F1F", "#A32D2D"),
    "SANGAT TIDAK SEHAT": ("#FCEBEB", "#501313", "#791F1F"),
    "BERBAHAYA":          ("#FCEBEB", "#501313", "#501313"),
}

# ── Chart tren rata-rata ISPU: tahun ini vs tahun lalu (jika data tersedia) ──
df_trend = df_home.copy()
df_trend["tanggal_lengkap"] = pd.to_datetime(df_trend["tanggal_lengkap"])
df_trend["tahun"] = df_trend["tanggal_lengkap"].dt.year
df_trend["bulan"] = df_trend["tanggal_lengkap"].dt.month

value_col_trend = ispu_col if ispu_col in df_trend.columns else "max"

tahun_tersedia = sorted(df_trend["tahun"].unique())
tahun_ini = tahun_tersedia[-1]
# Hanya bandingkan dengan tahun lalu kalau datanya memang tersedia —
# sebelumnya kalau cuma ada 1 tahun data, grafik menggambar 2 garis
# identik bertumpuk dengan label tahun yang sama, membingungkan.
tahun_lalu = tahun_tersedia[-2] if len(tahun_tersedia) > 1 else None

if tahun_lalu is not None:
    judul_trend = f"📈 Tren Rata-rata ISPU: {tahun_lalu} vs {tahun_ini}"
    caption_trend = (
        f"Rata-rata ISPU bulanan gabungan seluruh stasiun, membandingkan {tahun_lalu} dan {tahun_ini}. "
        "Garis putus-putus horizontal menandai ambang kategori BAIK (50), SEDANG (100), dan TIDAK SEHAT (200)."
    )
else:
    judul_trend = f"📈 Tren Rata-rata ISPU — {tahun_ini}"
    caption_trend = (
        f"Rata-rata ISPU bulanan gabungan seluruh stasiun untuk {tahun_ini} "
        "(data tahun sebelumnya belum tersedia untuk perbandingan). "
        "Garis putus-putus horizontal menandai ambang kategori BAIK (50), SEDANG (100), dan TIDAK SEHAT (200)."
    )

st.markdown(f"#### {judul_trend}")

bulan_label = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

with st.container(border=True):
    fig, ax = plt.subplots(figsize=(8, 3), dpi=160)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    garis_tahun = [(tahun_ini, "#1E9FDB", "-")]
    if tahun_lalu is not None:
        garis_tahun.insert(0, (tahun_lalu, "#9AAAC0", "--"))

    for tahun, warna, gaya in garis_tahun:
        subset = (
            df_trend[df_trend["tahun"] == tahun]
            .groupby("bulan")[value_col_trend]
            .mean()
            .reindex(range(1, 13))
        )
        ax.plot(
            range(1, 13), subset.values,
            color=warna, linewidth=2.2, linestyle=gaya,
            marker="o", markersize=4, label=str(tahun), zorder=3,
        )

    for y in (50, 100, 200):
        ax.axhline(y, color="#DDE4EE", linewidth=1, linestyle="--", zorder=1)

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(bulan_label, fontsize=8.5, color="#9AAAC0")
    ax.tick_params(axis="y", length=0, labelsize=8.5, colors="#9AAAC0")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_color("#DDE4EE")
    ax.spines["bottom"].set_color("#DDE4EE")
    ax.set_ylabel("Rata-rata ISPU", fontsize=9, color="#5B6E88")
    ax.legend(frameon=False, fontsize=9, loc="upper left", labelcolor="#1E2E42")
    fig.tight_layout()

    st.pyplot(fig, use_container_width=True)
    st.caption(caption_trend)

st.markdown(f"#### Status Tiap Stasiun per {tanggal_terkini}")

cols_home = st.columns(len(ringkasan_home))

for i, (_, row) in enumerate(ringkasan_home.iterrows()):
    with cols_home[i]:
        label = KATEGORI_DISPLAY.get(row["kategori"], row["kategori"])
        key = str(row["kategori"]).upper()
        badge_bg, badge_fg, accent = BADGE_STYLE.get(key, ("#F1EFE8", "#444441", "#888780"))

        nama = str(row["stasiun"])
        parts = nama.split(" ", 1)
        kode = parts[0] if len(parts) > 1 else ""
        nama_stn = parts[1] if len(parts) > 1 else nama

        content = f"""
            <p style="font-size:11px;color:#5B6E88;margin:8px 0 2px;">{kode}</p>
            <p style="font-size:13px;font-weight:500;color:#023E61;margin:0 0 10px;line-height:1.3;">{nama_stn}</p>
            <span style="display:inline-block;font-size:11px;font-weight:500;
                         padding:3px 10px;border-radius:99px;background:{badge_bg};color:{badge_fg};">{label}</span>
        """
        st.markdown(card(content, accent, radius="12px"), unsafe_allow_html=True)

# ── Insight singkat otomatis + navigasi cepat ──
if kategori_dominan.upper() in ["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]:
    st.warning(
        f"⚠️ Mayoritas stasiun berada pada kategori **{KATEGORI_DISPLAY.get(kategori_dominan, kategori_dominan)}**. "
        f"Kualitas udara paling buruk tercatat di **{stasiun_terburuk['stasiun']}**."
    )
else:
    st.success(
        f"✅ Secara umum kualitas udara berada pada kategori **{KATEGORI_DISPLAY.get(kategori_dominan, kategori_dominan)}**. "
        f"Stasiun dengan kualitas udara terbaik saat ini adalah **{stasiun_terbaik['stasiun']}**."
    )

nav1, nav2 = st.columns(2)
with nav1:
    st.markdown(
        card(
            """
            <p style="font-size:13px;font-weight:600;color:#023E61;margin:8px 0 4px;">📊 Visualisasi Data Historis</p>
            <p style="font-size:12px;color:#5B6E88;margin:0;">Lihat tren dan analisis data historis tiap stasiun secara lebih mendalam.</p>
            """,
            "#1E9FDB",
        ),
        unsafe_allow_html=True,
    )
with nav2:
    st.markdown(
        card(
            """
            <p style="font-size:13px;font-weight:600;color:#023E61;margin:8px 0 4px;">🔮 Prediksi 7 Hari</p>
            <p style="font-size:12px;color:#5B6E88;margin:0;">Lihat proyeksi kualitas udara H+1 s/d H+7 ke depan per stasiun.</p>
            """,
            "#1DB874",
        ),
        unsafe_allow_html=True,
    )
st.caption("↖️ Buka halaman-halaman tersebut lewat menu di sidebar.")

st.divider()

st.markdown("## 🧪 Unsur Kualitas Udara yang Dipantau")
st.caption("6 parameter polutan yang dipantau dan diprediksi oleh sistem")

# ── Data polutan: ringkasan + penyebab + cara menanggulangi ──
polutan_info = [
    (
        "PM2.5", "Partikel Halus", "≤ 2.5 µm",
        "Pembakaran kendaraan, industri, asap. Mudah masuk ke paru-paru.",
        "#E05C40",
        [
            "Emisi gas buang kendaraan bermotor, terutama mesin diesel",
            "Pembakaran biomassa, sampah, dan lahan terbuka",
            "Aktivitas industri dan pembangkit listrik berbahan bakar fosil",
            "Asap rokok dan aktivitas memasak dengan bahan bakar padat",
        ],
        [
            "Gunakan transportasi umum atau kendaraan rendah emisi",
            "Hindari membakar sampah atau lahan terbuka",
            "Gunakan masker N95 saat kualitas udara buruk",
            "Perbanyak ruang terbuka hijau di sekitar pemukiman",
        ],
    ),
    (
        "PM10", "Partikel Kasar", "≤ 10 µm",
        "Debu jalan, konstruksi, aktivitas mekanis. Ganggu saluran napas.",
        "#E8A020",
        [
            "Debu dari aktivitas konstruksi dan pembongkaran bangunan",
            "Jalan tidak beraspal serta kendaraan yang melintas",
            "Aktivitas pertambangan dan industri berat",
            "Angin yang menerbangkan partikel tanah kering",
        ],
        [
            "Penyiraman rutin pada area konstruksi dan jalan berdebu",
            "Menutup material dan bak truk pengangkut tanah/pasir",
            "Penyapuan jalan secara basah, bukan kering",
            "Penghijauan sebagai penahan debu alami",
        ],
    ),
    (
        "SO₂", "Sulfur Dioksida", "Gas",
        "Pembakaran bahan bakar fosil industri/pembangkit. Iritasi saluran napas.",
        "#1E9FDB",
        [
            "Pembakaran batu bara dan minyak bumi berkadar sulfur tinggi",
            "Aktivitas pembangkit listrik tenaga fosil (PLTU)",
            "Proses industri seperti peleburan logam dan kilang minyak",
        ],
        [
            "Pemasangan scrubber/alat penangkap sulfur pada cerobong industri",
            "Beralih ke bahan bakar rendah sulfur",
            "Mendorong transisi ke energi terbarukan",
            "Pengawasan dan penegakan baku mutu emisi industri",
        ],
    ),
    (
        "CO", "Karbon Monoksida", "Gas",
        "Pembakaran tidak sempurna kendaraan/genset. Kurangi oksigen darah.",
        "#5B6E88",
        [
            "Pembakaran tidak sempurna pada kendaraan bermotor",
            "Penggunaan genset dan mesin berbahan bakar di ruang tertutup",
            "Kompor gas dan perapian rumah tangga",
        ],
        [
            "Servis dan uji emisi kendaraan secara berkala",
            "Hindari menyalakan mesin/genset di ruang tertutup",
            "Pastikan ventilasi baik saat menggunakan alat pembakar",
            "Pasang detektor CO di area rawan seperti garasi tertutup",
        ],
    ),
    (
        "O₃", "Ozon", "Sekunder",
        "Reaksi fotokimia NOx + VOC dengan sinar matahari. Iritasi mata & napas.",
        "#1DB874",
        [
            "Reaksi fotokimia antara NOx dan senyawa organik volatil (VOC) di bawah sinar matahari",
            "Umumnya meningkat pada siang hari saat cuaca cerah dan terik",
            "Emisi kendaraan dan industri sebagai sumber gas prekursor",
        ],
        [
            "Menekan emisi NOx dan VOC dari kendaraan dan industri",
            "Gunakan produk rendah VOC seperti cat dan pelarut ramah lingkungan",
            "Kurangi aktivitas luar ruangan berat di siang hari saat ozon tinggi",
            "Perbanyak vegetasi yang menyerap polutan prekursor",
        ],
    ),
    (
        "NO₂", "Nitrogen Dioksida", "Gas",
        "Emisi kendaraan/industri. Perparah gangguan pernapasan.",
        "#0A6FA3",
        [
            "Emisi gas buang kendaraan bermotor, terutama di jalan padat",
            "Pembangkit listrik dan proses industri berbahan bakar fosil",
            "Pembakaran pada suhu tinggi secara umum",
        ],
        [
            "Transisi ke kendaraan listrik atau rendah emisi",
            "Penggunaan catalytic converter pada kendaraan",
            "Perluasan transportasi publik untuk kurangi kepadatan kendaraan",
            "Uji emisi kendaraan dan industri secara berkala",
        ],
    ),
]

cols_row1 = st.columns(3)
cols_row2 = st.columns(3)
all_cols = cols_row1 + cols_row2

for col, (simbol, nama, satuan, deskripsi, accent, _, _) in zip(all_cols, polutan_info):
    with col:
        content = f"""
            <div style="display:flex;align-items:baseline;gap:8px;margin:8px 0 2px;">
                <span style="font-size:22px;font-weight:700;color:{accent};">{simbol}</span>
                <span style="font-size:11px;color:#9AAAC0;text-transform:uppercase;
                             letter-spacing:0.04em;">{satuan}</span>
            </div>
            <p style="font-size:13px;font-weight:600;color:#1E2E42;margin:0 0 8px;">
                {nama}
            </p>
            <p style="font-size:12px;color:#5B6E88;line-height:1.5;margin:0;">
                {deskripsi}
            </p>
        """
        st.markdown(card(content, accent, height="180px"), unsafe_allow_html=True)

# ── Detail Penyebab & Cara Menanggulangi per polutan ──
st.markdown("#### 🔎 Penyebab & Cara Menanggulangi Tiap Polutan")

tab_labels = [f"{p[0]}" for p in polutan_info]
tabs = st.tabs(tab_labels)

for tab, (simbol, nama, satuan, deskripsi, accent, penyebab, penanggulangan) in zip(tabs, polutan_info):
    with tab:
        st.markdown(
            _flatten_html(f"""
            <p style="font-size:13px;color:#5B6E88;margin:4px 0 14px;">
                <span style="font-weight:700;color:{accent};">{simbol}</span> — {nama}
            </p>
            """),
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            items_html = "".join(f"<li style='margin-bottom:6px;'>{x}</li>" for x in penyebab)
            st.markdown(
                _flatten_html(f"""
                <div style="background:rgba(255,248,236,0.65);border-left:4px solid #E8A020;
                            border-radius:12px;padding:1rem 1.2rem;height:100%;">
                    <p style="font-size:12px;font-weight:700;color:#BA7517;margin:0 0 8px;
                              text-transform:uppercase;letter-spacing:0.04em;">
                        ⚠️ Penyebab
                    </p>
                    <ul style="margin:0;padding-left:1.1rem;font-size:13px;color:#1E2E42;line-height:1.5;">
                        {items_html}
                    </ul>
                </div>
                """),
                unsafe_allow_html=True
            )

        with c2:
            items_html = "".join(f"<li style='margin-bottom:6px;'>{x}</li>" for x in penanggulangan)
            st.markdown(
                _flatten_html(f"""
                <div style="background:rgba(93,212,160,0.18);border-left:4px solid #1DB874;
                            border-radius:12px;padding:1rem 1.2rem;height:100%;">
                    <p style="font-size:12px;font-weight:700;color:#1DB874;margin:0 0 8px;
                              text-transform:uppercase;letter-spacing:0.04em;">
                        ✅ Cara Menanggulangi
                    </p>
                    <ul style="margin:0;padding-left:1.1rem;font-size:13px;color:#1E2E42;line-height:1.5;">
                        {items_html}
                    </ul>
                </div>
                """),
                unsafe_allow_html=True
            )

# ─────────────────────────────────────────────
# FITUR PETA CAKUPAN STASIUN PEMANTAUAN
# ─────────────────────────────────────────────

st.markdown("## 🗺️ Cakupan Wilayah Stasiun Pemantauan")

st.write(
    "Pilih stasiun pemantauan untuk melihat wilayah yang menjadi cakupan "
    "pemantauan kualitas udara."
)

data_stasiun = {
    "DKI1 Bundaran HI": {
        "lokasi": "Jakarta Pusat",
        "wilayah": ["Menteng", "Tanah Abang", "Gambir", "Senen", "Sawah Besar"],
        "lat": -6.1944,
        "lon": 106.8231,
        "zoom": 13,
    },
    "DKI2 Kelapa Gading": {
        "lokasi": "Jakarta Utara",
        "wilayah": ["Kelapa Gading", "Tanjung Priok", "Koja", "Cilincing"],
        "lat": -6.1575,
        "lon": 106.9005,
        "zoom": 13,
    },
    "DKI3 Jagakarsa": {
        "lokasi": "Jakarta Selatan",
        "wilayah": ["Jagakarsa", "Pasar Minggu", "Cilandak", "Lenteng Agung"],
        "lat": -6.3349,
        "lon": 106.8248,
        "zoom": 13,
    },
    "DKI4 Lubang Buaya": {
        "lokasi": "Jakarta Timur",
        "wilayah": ["Cipayung", "Pondok Gede", "Kramat Jati", "Pasar Rebo"],
        "lat": -6.2930,
        "lon": 106.9070,
        "zoom": 13,
    },
    "DKI5 Kebon Jeruk": {
        "lokasi": "Jakarta Barat",
        "wilayah": ["Kebon Jeruk", "Palmerah", "Kembangan", "Grogol"],
        "lat": -6.1927,
        "lon": 106.7695,
        "zoom": 13,
    },
}

pilihan = st.selectbox("Pilih Stasiun Pemantauan", list(data_stasiun.keys()))
info = data_stasiun[pilihan]

col1, col2 = st.columns([1, 2])

with col1:
    wilayah_html = "".join(f"<li>{x}</li>" for x in info["wilayah"])
    info_content = f"""
        <p style="font-size:15px;font-weight:700;color:#023E61;margin:8px 0 10px;">📍 {pilihan}</p>
        <p style="font-size:11px;color:#9AAAC0;text-transform:uppercase;letter-spacing:0.05em;margin:0 0 4px;">Lokasi</p>
        <p style="font-size:13px;color:#1E2E42;margin:0 0 14px;">{info['lokasi']}</p>
        <p style="font-size:11px;color:#9AAAC0;text-transform:uppercase;letter-spacing:0.05em;margin:0 0 6px;">Wilayah yang dipantau</p>
        <ul style="margin:0;padding-left:1.1rem;font-size:13px;color:#1E2E42;line-height:1.6;">
            {wilayah_html}
        </ul>
    """
    st.markdown(card(info_content, "#1E9FDB", height="100%"), unsafe_allow_html=True)

with col2:
    m = folium.Map(location=[info["lat"], info["lon"]], zoom_start=info["zoom"])

    folium.Marker(
        [info["lat"], info["lon"]],
        popup=pilihan,
        tooltip="Lokasi Stasiun",
        icon=folium.Icon(color="blue", icon="cloud"),
    ).add_to(m)

    folium.Circle(
        radius=5000,
        location=[info["lat"], info["lon"]],
        popup="Perkiraan area cakupan pemantauan",
        color="blue",
        fill=True,
        fill_opacity=0.25,
    ).add_to(m)

    st_folium(m, width=700, height=500)

st.caption(
    f"Data: datasets/data_ispu_clean.csv | Sumber: ISPU DKI Jakarta | "
    f"Periode dataset: {tanggal_awal} s/d {tanggal_terkini}"
)