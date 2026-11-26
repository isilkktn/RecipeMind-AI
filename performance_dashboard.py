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

    with open(dosya_yolu, encoding="utf-8") as dosya:

        veriler = json.load(dosya)

    df = pd.DataFrame(veriler)

    # TOP 10 SONUCLARI

    top10_yolu = BASE / "performance_top10_metrics.json"

    top10_hazir = top10_yolu.exists()

    if top10_hazir:

        with open(top10_yolu, encoding="utf-8") as dosya:

            top10_veriler = json.load(dosya)

        top10_df = pd.DataFrame(top10_veriler)

        df = df.merge(

            top10_df[["yontem", "ndcg_at_10"]],

            on="yontem",

            how="left"

        )

    hibrit = df[
        df["yontem"] == "RecipeMind Hybrid"
    ].iloc[0]

    # OZET METRIKLER

    st.subheader("RecipeMind Hybrid Sonuçları")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Precision@5",
        f"%{hibrit['precision_at_5'] * 100:.0f}"
    )

    c2.metric(
        "nDCG@5",
        f"{hibrit['ndcg_at_5']:.4f}"
    )

    if top10_hazir:

        c3.metric(
            "nDCG@10",
            f"{hibrit['ndcg_at_10']:.4f}"
        )

    else:

        c3.metric("nDCG@10", "—")

    c4.metric(
        "Malzeme Uyumu",
        f"%{hibrit['malzeme_uyumu'] * 100:.2f}"
    )

    c5.metric(
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
        "ndcg_at_10": "nDCG@10",
        "malzeme_uyumu": "Malzeme Uyumu (%)",
        "arama_suresi_ms": "Arama Süresi (ms)"

    })

    st.dataframe(

        tablo.round(4),

        hide_index=True,

        width="stretch"

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

        if yuzde:

            olcek = alt.Scale(domain=[0, 100])

        elif sutun.startswith("ndcg"):

            olcek = alt.Scale(domain=[0, 1])

        else:

            olcek = alt.Scale(zero=True)

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

                scale=olcek

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

            width="stretch"

        )

    # BILGI ERISIMI METRIKLERI

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

    # NDCG TOP 10

    st.divider()

    st.subheader("nDCG@10 Performans Karşılaştırması")

    if top10_hazir:

        grafik(
            "ndcg_at_10",
            "nDCG@10"
        )

        st.caption(
            "İlk 10 sonucun ilgililik derecesi ve "
            "sıralama kalitesi değerlendirilmiştir. "
            "İdeal sıralama, değerlendirme havuzuna dayanır."
        )

    else:

        st.warning(
            "Top-10 performans sonuçları bulunamadı."
        )

    # MALZEME UYUMU

    st.divider()

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

    ) * 100 if bm25["malzeme_uyumu"] else None

    rrf_artis = (

        (
            hibrit["malzeme_uyumu"]
            - rrf["malzeme_uyumu"]
        )

        / rrf["malzeme_uyumu"]

    ) * 100 if rrf["malzeme_uyumu"] else None

    a1, a2 = st.columns(2)

    a1.metric(

        "BM25'e Göre Göreceli Artış",

        f"%{bm25_artis:.1f}"
        if bm25_artis is not None else "—"

    )

    a2.metric(

        "RRF'ye Göre Göreceli Artış",

        f"%{rrf_artis:.1f}"
        if rrf_artis is not None else "—"

    )

    # ARAMA SURESI

    st.divider()

    st.subheader("Arama Süresi Karşılaştırması")

    grafik(

        "arama_suresi_ms",

        "Süre (ms)"

    )

    st.caption(
        "Arama süreleri Top-5 deneyinden alınmıştır."
    )

    # AKADEMIK DEGERLENDIRME

    st.divider()

    st.subheader("Deneysel Bulgular")

    st.markdown("""

    RecipeMind Hybrid algoritması, BM25 ve anlamsal
    arama sonuçlarını Reciprocal Rank Fusion (RRF)
    yöntemiyle birleştirmekte ve malzeme uyumuna
    göre yeniden sıralamaktadır.

    Deney sonuçlarında BM25 genel ilgililik
    metriklerinde daha başarılı olurken,
    RecipeMind Hybrid malzeme uyumu açısından
    en yüksek performansı göstermiştir.

    Bu sonuç, hibrit yaklaşımın kullanıcıların
    mevcut malzemelerine uygun tarifleri
    önceliklendirme amacını desteklemektedir.

    """)

    if top10_hazir:

        st.markdown(f"""

        **Top-10 değerlendirmesinde:**

        - BM25 nDCG@10: {bm25['ndcg_at_10']:.4f}
        - RecipeMind Hybrid nDCG@10: {hibrit['ndcg_at_10']:.4f}
        - RRF nDCG@10: {rrf['ndcg_at_10']:.4f}

        Mevcut deneyde RecipeMind Hybrid,
        nDCG@10 metriğinde BM25'e yakın sonuç
        elde etmiş ve RRF ile anlamsal aramayı
        geride bırakmıştır.

        """)

    # DENEY SINIRLAMALARI

    with st.expander("Deney Yöntemi ve Sınırlamalar"):

        st.markdown("""

        - Veri seti: 10.499 yemek tarifi
        - Test sorgusu sayısı: 10
        - Karşılaştırılan algoritma sayısı: 4
        - Değerlendirme derinliği: Top-5 ve Top-10
        - Top-5 deneyinde 200 arama sonuç kaydı
        - Top-10 deneyinde 400 arama sonuç kaydı
        - İlgililik ölçeği: 0, 1 ve 2
        - İlgililik etiketleri yapay zekâ desteklidir.
        - Bağımsız insan değerlendirmesi yapılmamıştır.
        - Recall ve ideal nDCG sıralaması değerlendirme
          havuzuna göre hesaplanmıştır.
        - Malzeme uyumu metinsel eşleşmeye dayanır.
        - Malzeme miktarlarının yeterliliği ölçülmemiştir.
        - Arama süreleri model yükleme ve RAG yanıt
          üretim sürelerini kapsamamaktadır.
        - Sonuçlar sınırlı sayıdaki test sorgusuna
          dayanmaktadır.
        - Eş anlamlı ve kelime eşleşmeyen sorgular
          için ayrı deney henüz yapılmamıştır.

        """)


# BAGIMSIZ TEST

if __name__ == "__main__":

    st.set_page_config(

        page_title="RecipeMind AI - Performans",

        page_icon="📊",

        layout="wide"

    )

    performans_paneli()