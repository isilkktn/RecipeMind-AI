import json
import pandas as pd
import streamlit as st
import altair as alt

from pathlib import Path

BASE = Path(__file__).resolve().parent


def performans_paneli():

    st.header("Akademik Performans Analizi")

    st.markdown(
        "RecipeMind AI arama algoritmalarının "
        "deneysel performans karşılaştırması."
    )

    dosya_yolu = BASE / "performance_metrics.json"

    if not dosya_yolu.exists():

        st.warning("Performans sonuçları bulunamadı.")

        return

    with open(
        dosya_yolu,
        encoding="utf-8"
    ) as dosya:

        veriler = json.load(dosya)

    df = pd.DataFrame(veriler)

    hibrit = df[
        df["yontem"] == "RecipeMind Hybrid"
    ].iloc[0]

    # OZET METRIKLER

    st.subheader("RecipeMind Hybrid Sonuçları")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Precision@5",
        f"%{hibrit['precision_at_5'] * 100:.0f}"
    )

    c2.metric(
        "nDCG@5",
        f"{hibrit['ndcg_at_5']:.4f}"
    )

    c3.metric(
        "Malzeme Uyumu",
        f"%{hibrit['malzeme_uyumu'] * 100:.2f}"
    )

    c4.metric(
        "Arama Süresi",
        f"{hibrit['arama_suresi_ms']:.2f} ms"
    )

    st.divider()

    # KARSILASTIRMA TABLOSU

    st.subheader("Algoritma Karşılaştırma Tablosu")

    tablo = df.copy()

    for sutun in [
        "precision_at_5",
        "recall_at_5",
        "f1_at_5",
        "malzeme_uyumu"
    ]:

        tablo[sutun] = tablo[sutun] * 100

    tablo = tablo.rename(columns={

        "yontem": "Algoritma",
        "test_sayisi": "Test Sayısı",
        "precision_at_5": "Precision@5 (%)",
        "recall_at_5": "Recall@5 Havuz (%)",
        "f1_at_5": "F1@5 (%)",
        "ndcg_at_5": "nDCG@5",
        "malzeme_uyumu": "Malzeme Uyumu (%)",
        "arama_suresi_ms": "Arama Süresi (ms)"

    })

    st.dataframe(
        tablo.round(4),
        hide_index=True,
        use_container_width=True
    )

    # GRAFIK FONKSIYONU

    def grafik(sutun, baslik, yuzde=False):

        grafik_df = df[
            ["yontem", sutun]
        ].copy()

        if yuzde:

            grafik_df[sutun] *= 100

        grafik_df = grafik_df.rename(
            columns={sutun: "deger"}
        )

        chart = alt.Chart(
            grafik_df
        ).mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        ).encode(

            x=alt.X(
                "yontem:N",
                title="Algoritma",
                sort=None,
                axis=alt.Axis(labelAngle=-15)
            ),

            y=alt.Y(
                "deger:Q",
                title=baslik,
                scale=alt.Scale(
                    domain=[0, 100]
                ) if yuzde else alt.Scale(
                    zero=True
                )
            ),

            color=alt.condition(
                alt.datum.yontem == "RecipeMind Hybrid",
                alt.value("#38583F"),
                alt.value("#B9C8B5")
            ),

            tooltip=[

                alt.Tooltip(
                    "yontem:N",
                    title="Algoritma"
                ),

                alt.Tooltip(
                    "deger:Q",
                    title=baslik,
                    format=".4f"
                )

            ]

        ).properties(
            height=280
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

    # PERFORMANS GRAFIKLERI

    st.divider()

    st.subheader("Bilgi Erişimi Metrikleri")

    g1, g2 = st.columns(2)

    with g1:

        st.markdown("**Precision@5**")

        grafik(
            "precision_at_5",
            "Precision (%)",
            True
        )

    with g2:

        st.markdown("**Recall@5**")

        grafik(
            "recall_at_5",
            "Havuz Recall (%)",
            True
        )

    g3, g4 = st.columns(2)

    with g3:

        st.markdown("**F1-Score@5**")

        grafik(
            "f1_at_5",
            "F1-Score (%)",
            True
        )

    with g4:

        st.markdown("**nDCG@5**")

        grafik(
            "ndcg_at_5",
            "nDCG@5"
        )

    st.divider()

    # MALZEME UYUMU

    st.subheader("Malzeme Uyumu Karşılaştırması")

    grafik(
        "malzeme_uyumu",
        "Malzeme Uyumu (%)",
        True
    )

    bm25 = df[
        df["yontem"] == "BM25"
    ].iloc[0]

    rrf = df[
        df["yontem"] == "RRF"
    ].iloc[0]

    bm25_artis = (
        (
            hibrit["malzeme_uyumu"]
            - bm25["malzeme_uyumu"]
        )
        / bm25["malzeme_uyumu"]
    ) * 100

    rrf_artis = (
        (
            hibrit["malzeme_uyumu"]
            - rrf["malzeme_uyumu"]
        )
        / rrf["malzeme_uyumu"]
    ) * 100

    a1, a2 = st.columns(2)

    a1.metric(
        "BM25'e Göre Göreceli Artış",
        f"%{bm25_artis:.1f}"
    )

    a2.metric(
        "RRF'ye Göre Göreceli Artış",
        f"%{rrf_artis:.1f}"
    )

    # ARAMA SURESI

    st.divider()

    st.subheader("Arama Süresi Karşılaştırması")

    grafik(
        "arama_suresi_ms",
        "Süre (ms)"
    )

    # AKADEMIK DEGERLENDIRME

    st.divider()

    st.subheader("Deneysel Bulgular")

    st.markdown("""

    RecipeMind Hybrid algoritması, BM25 ve
    anlamsal arama sonuçlarını Reciprocal Rank
    Fusion (RRF) yöntemiyle birleştirmekte ve
    malzeme uyumuna göre yeniden sıralamaktadır.

    Deney sonuçlarında BM25 genel ilgililik
    metriklerinde daha başarılı olurken,
    RecipeMind Hybrid malzeme uyumu açısından
    en yüksek performansı göstermiştir.

    Bu sonuç, hibrit yaklaşımın kullanıcıların
    mevcut malzemelerine uygun tarifleri
    önceliklendirme amacını desteklemektedir.

    """)

    with st.expander("Deney Yöntemi ve Sınırlamalar"):

        st.markdown("""

        - Veri seti: 10.499 yemek tarifi
        - Test sorgusu sayısı: 10
        - Karşılaştırılan algoritma sayısı: 4
        - Değerlendirme derinliği: Top-5
        - İlgililik ölçeği: 0, 1 ve 2
        - İlgililik etiketleri yapay zekâ desteklidir.
        - Bağımsız insan değerlendirmesi yapılmamıştır.
        - Recall, değerlendirme havuzuna göre hesaplanmıştır.
        - Malzeme uyumu, metinsel malzeme eşleşmesine dayanır.
        - Arama süresi, model yükleme ve RAG yanıt
          üretim sürelerini kapsamamaktadır.
        - Sonuçlar sınırlı sayıdaki test sorgusuna
          dayanmaktadır.

        """)


# BAGIMSIZ TEST

if __name__ == "__main__":

    st.set_page_config(

        page_title="RecipeMind AI - Performans",

        page_icon="📊",

        layout="wide"

    )

    performans_paneli()