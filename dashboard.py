import streamlit as st

pg = st.navigation(
    [
        st.Page(
            "pages/0_🏠_Ringkasan_Eksekutif.py",
            title="Ringkasan Eksekutif",
            icon="🏠",
        ),
        st.Page(
            "pages/1_📊_Visualisasi_Kualitas_Udara.py",
            title="Visualisasi Data Historis",
            icon="📊",
        ),
        st.Page(
            "pages/2_🔮_Prediksi_Kualitas_Udara_7_Hari.py",
            title="Prediksi Kualitas Udara H+7",
            icon="🔮",
        ),
    ]
)

pg.run()