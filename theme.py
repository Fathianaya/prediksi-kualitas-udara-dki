"""
theme.py — panggil apply_theme() di awal setiap halaman Streamlit
agar style konsisten di seluruh aplikasi.
"""
import streamlit as st


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Root palette ── */
:root {
    --sky-50:   #EFF8FF;
    --sky-100:  #C9E9FF;
    --sky-300:  #67C0F5;
    --sky-500:  #1E9FDB;
    --sky-700:  #0A6FA3;
    --sky-900:  #023E61;
    --mint-50:  #EDFAF4;
    --mint-300: #5DD4A0;
    --mint-500: #1DB874;
    --amber-50: #FFF8EC;
    --amber-400:#E8A020;
    --red-50:   #FFF1EE;
    --red-400:  #E05C40;
    --gray-50:  #F8FAFC;
    --gray-100: #EFF3F8;
    --gray-200: #DDE4EE;
    --gray-400: #9AAAC0;
    --gray-600: #5B6E88;
    --gray-800: #1E2E42;
}

/* ── Force light color scheme ── */
html, body { color-scheme: light !important; }

/* ── Base — paksa SEMUA teks jadi gelap ── */
html, body,
.main, .main *,
[data-testid="stAppViewContainer"] *,
[data-testid="stVerticalBlock"] *,
[data-testid="stHeader"] *,
[data-testid="stToolbar"] *,
p, h1, h2, h3, h4, h5, h6,
span, div, label, small, li, td, th, button {
    font-family: 'DM Sans', sans-serif !important;
    color: #1E2E42 !important;
}

/* ── Jangan timpa font ikon Material Symbols ──
   Aturan di atas ("[data-testid=\"stHeader\"] *", dst) ikut menimpa
   font-family elemen ikon bawaan Streamlit (mis. tombol collapse
   sidebar), sehingga nama ligature-nya ("keyboard_double_arrow_left")
   muncul sebagai teks polos alih-alih jadi glyph panah.
   Kembalikan font khusus untuk elemen ikon di sini — hanya font-family
   yang diubah, warna tetap ikut aturan lain di atas. */
[data-testid="stIconMaterial"],
[data-testid="stHeader"] [data-testid="stIconMaterial"],
[data-testid="stToolbar"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}

/* ── Page background ── */
.stApp {
    background: linear-gradient(165deg, #EFF8FF 0%, #F0FAF5 50%, #FAFCFF 100%) !important;
    min-height: 100vh;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        radial-gradient(ellipse 600px 300px at 10% 20%, rgba(103,192,245,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 400px 250px at 85% 60%, rgba(29,184,116,0.08) 0%, transparent 70%),
        radial-gradient(ellipse 500px 200px at 50% 85%, rgba(30,159,219,0.07) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #023E61 0%, #0A4A72 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"],
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] li { color: #C9E9FF !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }
[data-testid="stSidebar"] a:hover { color: #ffffff !important; }

/* ── Main container ── */
.main .block-container {
    padding: 2.5rem 3rem 3rem !important;
    max-width: 1200px;
}

/* ── Headings ── */
h1 {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #023E61 !important;
    letter-spacing: -0.03em;
    line-height: 1.15 !important;
    margin-bottom: 0.2rem !important;
}
h1::after {
    content: "";
    display: block;
    width: 56px;
    height: 3px;
    border-radius: 2px;
    background: linear-gradient(90deg, #1E9FDB, #1DB874);
    margin-top: 10px;
}
h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #023E61 !important;
}

/* ── Subheader ── */
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3 {
    font-size: 1.15rem !important;
    font-weight: 600 !important;
    color: #0A6FA3 !important;
    border-bottom: 1px solid #DDE4EE;
    padding-bottom: 6px;
    margin-bottom: 1rem !important;
}

/* ── Markdown ── */
.stMarkdown p { color: #5B6E88 !important; font-size: 0.97rem !important; line-height: 1.75 !important; }
.stMarkdown strong { color: #0A6FA3 !important; font-weight: 600 !important; }
.stMarkdown li { color: #5B6E88 !important; }

/* ── Markdown table ── */
.stMarkdown table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: rgba(255,255,255,0.85) !important;
    border: 1px solid #DDE4EE !important;
    border-radius: 12px !important;
    overflow: hidden;
    margin: 1.25rem 0 !important;
    box-shadow: 0 2px 12px rgba(10,111,163,0.07);
}
.stMarkdown th {
    background: linear-gradient(90deg, #EFF8FF, #EDFAF4) !important;
    color: #0A6FA3 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 0.75rem 1.1rem !important;
    border-bottom: 1px solid #DDE4EE !important;
}
.stMarkdown td { color: #1E2E42 !important; padding: 0.65rem 1.1rem !important; font-size: 0.95rem !important; border-bottom: 1px solid #EFF3F8 !important; }
.stMarkdown tr:last-child td { border-bottom: none !important; }

/* ── Alert / info / warning / success ── */
[data-testid="stAlert"] {
    border-radius: 14px !important;
    border-width: 0 0 0 4px !important;
    padding: 1rem 1.25rem !important;
    font-size: 0.92rem !important;
    line-height: 1.6;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span { color: #1E2E42 !important; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.8) !important;
    border: 1px solid #DDE4EE !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 2px 8px rgba(10,111,163,0.06);
    min-height: 100px;
}
[data-testid="stMetricLabel"] { color: #5B6E88 !important; }
[data-testid="stMetricLabel"] p { color: #5B6E88 !important; font-size: 0.82rem !important; }

/* Nilai metric: dibiarkan wrap ke baris baru agar tidak terpotong "..." */
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {
    color: #023E61 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
    font-size: 1.4rem !important;
    line-height: 1.25 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; }

/* ── Selectbox & multiselect sidebar ── */

[data-testid="stSidebar"] [data-baseweb="select"] > div {

    background: rgba(255,255,255,0.12) !important;

    border:1px solid rgba(255,255,255,0.3) !important;

    border-radius:8px !important;

}


/* teks input multiselect */

[data-testid="stSidebar"] [data-baseweb="select"] input {

    color:#ffffff !important;

}


/* area pilihan yang sudah dipilih */

[data-testid="stSidebar"] [data-baseweb="tag"] {

    background:#1E9FDB !important;

    border-radius:6px !important;

}


/* teks dalam tag */

[data-testid="stSidebar"] [data-baseweb="tag"] span {

    color:#ffffff !important;

}


/* tombol hapus x */

[data-testid="stSidebar"] [data-baseweb="tag"] svg {

    fill:#ffffff !important;

}


/* =========================
   DROPDOWN MULTISELECT
   ========================= */


[data-testid="stSidebar"] [data-baseweb="popover"] {

    background:#023E61 !important;

}


[data-testid="stSidebar"] [data-baseweb="menu"] {

    background:#023E61 !important;

}


/* pilihan dropdown */

[data-testid="stSidebar"] [role="option"] {

    background:#023E61 !important;

    color:#ffffff !important;

}


/* hover pilihan */

[data-testid="stSidebar"] [role="option"]:hover {

    background:#0A6FA3 !important;

}


/* tulisan No results */

[data-testid="stSidebar"] [data-baseweb="menu"] div {

    color:#ffffff !important;

}

/* ── Tombol di sidebar (mis. "Pilih Semua" / "Hapus Semua") ── */
[data-testid="stSidebar"] .stButton button,
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-weight: 500 !important;
    transition: background 0.15s ease, border-color 0.15s ease;
}
[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span,
[data-testid="stSidebar"] .stButton button div {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: #ffffff !important;
}
[data-testid="stSidebar"] .stButton button:active {
    background: rgba(255,255,255,0.25) !important;
}

/* ── Date input di sidebar ── */
[data-testid="stSidebar"] input {
    color: #1E2E42 !important;
    background-color: #ffffff !important;
}


[data-testid="stSidebar"] [data-baseweb="input"] {
    background-color: #ffffff !important;
}


[data-testid="stSidebar"] [data-baseweb="input"] input {
    color: #1E2E42 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid #DDE4EE !important;
    box-shadow: 0 2px 8px rgba(10,111,163,0.06);
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #DDE4EE !important;
    margin: 1.5rem 0 !important;
}

/* ── Caption ── */
.stCaption, [data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p { color: #9AAAC0 !important; font-size: 0.78rem !important; }

/* ── Plotly bg transparent ── */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #EFF3F8; }
::-webkit-scrollbar-thumb { background: #67C0F5; border-radius: 3px; }
</style>
"""


def apply_theme():
    """Inject the global air-quality theme CSS. Call once per page, before any content."""
    st.markdown(_CSS, unsafe_allow_html=True)