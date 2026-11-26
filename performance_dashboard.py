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

    def grafik(
        sutun,
        baslik,
        yuzde=False,
        veri=None,
        vurgulanan="RecipeMind Hybrid"
    ):

        kaynak = df if veri is None else veri

        grafik_df = kaynak[
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
                alt.datum.yontem == vurgulanan,
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

        ).properties(height=280)

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
            "İdeal sıralama değerlendirme havuzuna dayanır."
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
        "Arama süreleri genel Top-5 deneyinden alınmıştır."
    )

    # ANLAMSAL SORGU DENEYI

    st.divider()

    st.header("Anlamsal Sorgu Deneyi")

    st.markdown(
        "Bu deneyde doğal dilde ifade edilen 10 farklı "
        "kullanıcı sorgusu üzerinden BM25 ve anlamsal "
        "arama yöntemleri karşılaştırılmıştır."
    )

    semantic_yolu = (
        BASE / "semantic_performance_metrics.json"
    )

    semantic_hazir = semantic_yolu.exists()

    if semantic_hazir:

        with open(
            semantic_yolu,
            encoding="utf-8"
        ) as dosya:

            semantic_veriler = json.load(dosya)

        semantic_df = pd.DataFrame(semantic_veriler)

        semantic_bm25 = semantic_df[
            semantic_df["yontem"] == "BM25"
        ].iloc[0]

        semantic_model = semantic_df[
            semantic_df["yontem"] == "Semantic Search"
        ].iloc[0]

        # ANLAMSAL DENEY OZETI

        s1, s2, s3, s4 = st.columns(4)

        s1.metric(
            "Test Sorgusu",
            int(semantic_model["test_sayisi"])
        )

        s2.metric(
            "Anlamsal Precision@5",
            f"%{semantic_model['precision_at_5'] * 100:.0f}"
        )

        s3.metric(
            "Anlamsal nDCG@5",
            f"{semantic_model['ndcg_at_5']:.4f}"
        )

        s4.metric(
            "Anlamsal Arama Süresi",
            f"{semantic_model['arama_suresi_ms']:.2f} ms"
        )

        # ANLAMSAL DENEY TABLOSU

        st.subheader(
            "BM25 ve Anlamsal Arama Karşılaştırması"
        )

        semantic_tablo = semantic_df.copy()

        semantic_tablo["precision_at_5"] *= 100

        semantic_tablo = semantic_tablo.rename(
            columns={

                "yontem": "Algoritma",
                "test_sayisi": "Test Sayısı",
                "precision_at_5": "Precision@5 (%)",
                "ndcg_at_5": "nDCG@5",
                "arama_suresi_ms": "Arama Süresi (ms)",
                "sure_olculen_sorgu_sayisi":
                    "Süresi Ölçülen Sorgu Sayısı"

            }
        )

        st.dataframe(
            semantic_tablo.round(4),
            hide_index=True,
            width="stretch"
        )

        # ANLAMSAL DENEY GRAFIKLERI

        sg1, sg2 = st.columns(2)

        with sg1:

            st.markdown("**Precision@5**")

            grafik(
                "precision_at_5",
                "Precision (%)",
                True,
                veri=semantic_df,
                vurgulanan="Semantic Search"
            )

        with sg2:

            st.markdown("**nDCG@5**")

            grafik(
                "ndcg_at_5",
                "nDCG@5",
                veri=semantic_df,
                vurgulanan="Semantic Search"
            )

        st.markdown("**Arama Süresi Karşılaştırması**")

        grafik(
            "arama_suresi_ms",
            "Süre (ms)",
            veri=semantic_df,
            vurgulanan="Semantic Search"
        )

        # GORECELI PERFORMANS ARTISI

        precision_farki = (

            semantic_model["precision_at_5"]
            - semantic_bm25["precision_at_5"]

        ) * 100

        ndcg_artisi = (

            (
                semantic_model["ndcg_at_5"]
                - semantic_bm25["ndcg_at_5"]
            )

            / semantic_bm25["ndcg_at_5"]

        ) * 100 if semantic_bm25["ndcg_at_5"] else None

        sa1, sa2 = st.columns(2)

        sa1.metric(
            "Precision Farkı",
            f"{precision_farki:+.1f} yüzde puan"
        )

        sa2.metric(
            "nDCG Göreceli Değişimi",
            f"%{ndcg_artisi:.1f}"
            if ndcg_artisi is not None else "—"
        )

        # ANLAMSAL DENEY BULGULARI

        st.subheader("Anlamsal Arama Bulguları")

        if (
            semantic_model["precision_at_5"]
            > semantic_bm25["precision_at_5"]
            and semantic_model["ndcg_at_5"]
            > semantic_bm25["ndcg_at_5"]
        ):

            st.markdown(
                "Bu deneyde anlamsal arama yöntemi "
                "Precision@5 ve nDCG@5 metriklerinde "
                "BM25 yönteminden daha yüksek sonuç "
                "elde etmiştir."
            )

        st.markdown("""

        **Olumlu örnek:**

        Hastayken içimi ısıtacak bir yemek sorgusunda
        anlamsal arama, çorba türünde tarifler
        getirebilmiştir.

        **Olumsuz örnek:**

        Et içermeyen doyurucu yemek sorgusunda
        anlamsal arama etli tarifler de önermiştir.

        Bu durum modelin olumsuz ifadeleri ve
        kesin malzeme kısıtlamalarını anlamakta
        zorlanabildiğini göstermektedir.

        """)

        with st.expander(
            "Anlamsal Deney Yöntemi ve Sınırlamalar"
        ):

            st.markdown("""

            - Test sorgusu sayısı: 10
            - Karşılaştırılan yöntem sayısı: 2
            - Değerlendirme derinliği: Top-5
            - Toplam arama sonuç kaydı: 96
            - Tekrarsız sorgu-tarif eşleşmesi: 92
            - İlgililik ölçeği: 0, 1 ve 2
            - İlgililik etiketleri yapay zekâ desteklidir.
            - Bağımsız insan değerlendirmesi yapılmamıştır.
            - Precision@5 hesabında eksik sonuçlar
              ilgili kabul edilmemiştir.
            - nDCG ideal sıralaması değerlendirme
              havuzuna dayanır.
            - Sorguların tamamının kelime eşleşmesinden
              bağımsız olduğu doğrulanmamıştır.
            - Sorgularda Türkçe karakterler yerine
              ASCII karakterler kullanılmıştır.
            - Hiç sonuç getirilmeyen sorguların süreleri
              mevcut sonuç kayıtlarından hesaplanamaz.
            - Deney sonuçları bütün sorgu türlerine
              genellenemez.

            """)

    else:

        st.warning(
            "Anlamsal arama deney sonuçları bulunamadı."
        )

    # AKADEMIK DEGERLENDIRME

    st.divider()

    st.subheader("Genel Deneysel Bulgular")

    st.markdown("""

    RecipeMind Hybrid algoritması, BM25 ve anlamsal
    arama sonuçlarını Reciprocal Rank Fusion (RRF)
    yöntemiyle birleştirmekte ve malzeme uyumuna
    göre yeniden sıralamaktadır.

    Genel arama deneyinde BM25 ilgililik
    metriklerinde daha başarılı olurken,
    RecipeMind Hybrid malzeme uyumu açısından
    en yüksek performansı göstermiştir.

    Bu sonuç, hibrit yaklaşımın kullanıcıların
    mevcut malzemelerine uygun tarifleri
    önceliklendirme amacını desteklemektedir.

    """)

    if top10_hazir:

        st.markdown(f"""

        **Top-10 değerlendirmesi:**

        - BM25 nDCG@10: {bm25['ndcg_at_10']:.4f}
        - RecipeMind Hybrid nDCG@10: {hibrit['ndcg_at_10']:.4f}
        - RRF nDCG@10: {rrf['ndcg_at_10']:.4f}

        RecipeMind Hybrid, mevcut deneyde nDCG@10
        metriğinde BM25'e yakın bir sonuç elde
        etmiştir.

        """)

    if semantic_hazir:

        st.markdown(f"""

        **Anlamsal sorgu değerlendirmesi:**

        - BM25 Precision@5:
          %{semantic_bm25['precision_at_5'] * 100:.0f}

        - Semantic Search Precision@5:
          %{semantic_model['precision_at_5'] * 100:.0f}

        - BM25 nDCG@5:
          {semantic_bm25['ndcg_at_5']:.4f}

        - Semantic Search nDCG@5:
          {semantic_model['ndcg_at_5']:.4f}

        Genel arama ve anlamsal sorgu deneyleri,
        farklı test sorguları üzerinden yapılmıştır.
        Sonuçlar kendi deney kapsamlarında
        değerlendirilmelidir.

        """)

    # DENEY SINIRLAMALARI

    with st.expander("Genel Deney Yöntemi ve Sınırlamalar"):

        st.markdown("""

        - Veri seti: 10.499 yemek tarifi
        - Genel deney: 10 test sorgusu
        - Genel deneyde karşılaştırılan yöntem: 4
        - Değerlendirme derinliği: Top-5 ve Top-10
        - Top-5 deneyinde 200 arama sonuç kaydı
        - Top-10 deneyinde 400 arama sonuç kaydı
        - Anlamsal sorgu deneyinde 10 ek test sorgusu
        - Anlamsal deneyde karşılaştırılan yöntem: 2
        - İlgililik ölçeği: 0, 1 ve 2
        - İlgililik etiketleri yapay zekâ desteklidir.
        - Bağımsız insan değerlendirmesi yapılmamıştır.
        - Recall ve ideal nDCG sıralaması değerlendirme
          havuzuna göre hesaplanmıştır.
        - Malzeme uyumu metinsel eşleşmeye dayanır.
        - Malzeme miktarlarının yeterliliği ölçülmemiştir.
        - Arama süreleri model yükleme ve RAG yanıt
          üretim sürelerini kapsamamaktadır.
        - Anlamsal sorgu deneyi yapılmıştır ancak
          kesin eş anlamlılık ve sıfır kelime eşleşmesi
          ayrı olarak doğrulanmamıştır.
        - Sonuçlar sınırlı sayıdaki test sorgusuna
          dayanmaktadır.
        - Gıda israfındaki gerçek azalma ölçülmemiştir.

        """)


# BAGIMSIZ TEST

if __name__ == "__main__":

    st.set_page_config(
        page_title="RecipeMind AI - Performans",
        page_icon="📊",
        layout="wide"
    )

    performans_paneli()