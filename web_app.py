import streamlit as st
import json
import re
import torch
import faiss
import numpy as np

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

# SAYFA AYARLARI

st.set_page_config(
    page_title="RecipeMind-AI",
    page_icon="🍃",
    layout="wide"
)

# ARAYUZ TASARIMI

st.markdown("""
<style>

.stApp {
    background-color: #F6F8F3;
    color: #20382B;
}

[data-testid="stHeader"] {
    background-color: #F6F8F3;
}

[data-testid="stSidebar"] {
    background-color: #173D2B;
}

[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: #173D2B !important;
    font-weight: 700 !important;
}

p, label {
    color: #20382B !important;
    font-size: 16px;
}

[data-testid="stWidgetLabel"] p {
    color: #173D2B !important;
    font-weight: 600;
}

.stTextInput input {
    background-color: #FFFFFF !important;
    color: #173D2B !important;
    padding: 14px;
    font-size: 16px;
}

.stTextInput input::placeholder {
    color: #68786D !important;
}

[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border: 1px solid #A8BDAF !important;
    border-radius: 12px !important;
}

.stButton > button {
    background-color: #26734D !important;
    color: #FFFFFF !important;
    border: none;
    border-radius: 12px;
    padding: 14px 24px;
    font-size: 17px;
    font-weight: 600;
    width: 100%;
}

.stButton > button p {
    color: white !important;
}

.stButton > button:hover {
    background-color: #173D2B !important;
}

[data-testid="stMetricValue"] {
    color: #26734D !important;
    font-weight: bold;
}

[data-testid="stCaptionContainer"] p {
    color: #52675A !important;
}

[data-testid="stExpander"] {
    background-color: #FFFFFF;
    border-radius: 12px;
}

[data-testid="stExpander"] summary {
    color: #173D2B !important;
}

[data-testid="stExpander"] summary svg {
    color: #173D2B !important;
}

[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlockBorderWrapper"] > div {
    border-radius: 18px;
}

[data-testid="stAlert"] {
    background-color: #E7F3E9 !important;
}

.hero {
    background: linear-gradient(
        120deg, #173D2B, #36865B
    );
    padding: 40px;
    border-radius: 24px;
    margin-bottom: 28px;
}

.hero h1 {
    color: white !important;
    font-size: 45px;
    margin: 0;
}

.hero p {
    color: #E1F1E4 !important;
    font-size: 18px;
    margin-top: 12px;
}

.hero-tag {
    display: inline-block;
    background-color: #FFFFFF22;
    color: white;
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 14px;
    margin-bottom: 15px;
}

.recipe-card {
    background-color: #FFFFFF;
    border: 1px solid #DCE6DC;
    border-radius: 18px;
    padding: 24px;
    margin-top: 20px;
    box-shadow: 0 4px 15px #173D2B0A;
}

.recipe-title {
    color: #173D2B;
    font-size: 25px;
    font-weight: 700;
}

.recipe-category {
    color: #52705C;
    font-size: 14px;
    margin-top: 6px;
}

.footer {
    text-align: center;
    color: #52675A;
    padding: 25px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ANA BASLIK

st.markdown("""
<div class="hero">
    <div class="hero-tag">
        YAPAY ZEKA DESTEKLI AKILLI MUTFAK
    </div>
    <h1>🍃 RecipeMind-AI</h1>
    <p>
        Mutfağındaki malzemeler, yeni tariflere dönüşsün.
    </p>
    <p>
        Elindeki malzemeleri keşfet,
        sana uygun tarifleri bul ve gıda israfını azalt.
    </p>
</div>
""", unsafe_allow_html=True)


# METIN TEMIZLEME

def temizle(metin):
    return metin.replace(
        "I", "ı"
    ).replace("İ", "i").lower()


def kelimelere_ayir(metin):
    return re.findall(r"\w+", temizle(metin))


# ARAMA SISTEMINI YUKLEME

@st.cache_resource
def sistemi_yukle():

    with open(
        "data/test.jsonl",
        "r",
        encoding="utf-8"
    ) as dosya:

        tarifler = [
            json.loads(satir)
            for satir in dosya
            if satir.strip()
        ]

    model = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2",
        local_files_only=True
    )

    vektorler = torch.load(
        "data/vektorler.pt",
        map_location="cpu",
        weights_only=True
    ).numpy().astype("float32")

    if len(vektorler) != len(tarifler):
        raise ValueError(
            "Tarif ve vektör sayıları uyuşmuyor."
        )

    faiss.normalize_L2(vektorler)

    index = faiss.IndexFlatIP(
        vektorler.shape[1]
    )

    index.add(vektorler)

    metinler = [
        str(t.get("title", "")) + " " +
        str(t.get("ingredients", "")) + " " +
        str(t.get("description", ""))
        for t in tarifler
    ]

    bm25 = BM25Okapi([
        kelimelere_ayir(m)
        for m in metinler
    ])

    return tarifler, model, index, bm25


with st.spinner("Akıllı mutfak hazırlanıyor..."):

    tarifler, model, index, bm25 = sistemi_yukle()


# SOL MENU

with st.sidebar:

    st.title("🍃 RecipeMind")

    st.write("Akıllı Tarif Asistanı")

    st.divider()

    st.metric(
        "Veri tabanındaki tarifler",
        f"{len(tarifler):,}".replace(",", ".")
    )

    st.divider()

    st.subheader("Arama Teknolojileri")

    st.write("✅ BM25")
    st.write("✅ Anlamsal Arama")
    st.write("✅ FAISS")
    st.write("✅ RRF")
    st.write("✅ Malzeme Eşleştirme")

    st.divider()

    st.subheader("🌱 Amacımız")

    st.write(
        "Evdeki malzemeleri değerlendirerek "
        "gıda israfını azaltmak ve yemek "
        "seçimini kolaylaştırmak."
    )


# UST BILGI ALANI

col1, col2, col3 = st.columns(3)

col1.metric(
    "🍲 Yemek Tarifi",
    f"{len(tarifler):,}".replace(",", ".")
)

col2.metric(
    "🔍 Arama Yöntemi",
    "Hibrit"
)

col3.metric(
    "🌍 Uygulama Dili",
    "Türkçe"
)

st.divider()

# KULLANICI GIRIS ALANI

st.header("👩‍🍳 Bugün ne pişirelim?")

st.write(
    "Elindeki malzemeleri ve yemek tercihini "
    "gir, sana uygun tarifleri bulalım."
)

with st.form("tarif_formu"):

    giris = st.text_input(
        "🥕 Mutfağında hangi malzemeler var?",
        placeholder="Patates, yumurta, peynir, tuz"
    )

    sorgu = st.text_input(
        "🍽️ Nasıl bir yemek yapmak istersin?",
        placeholder="Kolay ve pratik bir kahvaltı"
    )

    sonuc_sayisi = st.selectbox(
        "Kaç tarif görmek istersin?",
        [3, 5, 10],
        index=1
    )

    ara = st.form_submit_button(
        "🔍 Bana Tarif Bul",
        use_container_width=True
    )


# ARAMA MOTORU

def tarif_ara(malzemeler, sorgu):

    bm25_puanlari = bm25.get_scores(
        kelimelere_ayir(sorgu)
    )

    bm25_siralama = [
        i for i in np.argsort(
            bm25_puanlari
        )[::-1]
        if bm25_puanlari[i] > 0
    ][:100]

    sorgu_vektoru = np.array(
        model.encode([sorgu]),
        dtype="float32"
    )

    faiss.normalize_L2(sorgu_vektoru)

    puanlar, indeksler = index.search(
        sorgu_vektoru, 100
    )

    rrf_puanlari = {}

    for siralama in [
        bm25_siralama,
        indeksler[0]
    ]:

        for sira, i in enumerate(
            siralama, start=1
        ):

            if i >= 0:

                rrf_puanlari[i] = (
                    rrf_puanlari.get(i, 0)
                    + 1 / (60 + sira)
                )

    sonuclar = []

    for i, rrf_puani in rrf_puanlari.items():

        tarif = tarifler[i]

        gerekli = tarif.get(
            "ingredients"
        ) or []

        mevcut = []
        eksik = []

        for g in gerekli:

            if any(
                re.search(
                    r"\b" + re.escape(m) + r"\b",
                    temizle(g)
                )
                for m in malzemeler
            ):

                mevcut.append(g)

            else:

                eksik.append(g)

        uyum = len(mevcut) / max(
            len(gerekli), 1
        )

        final_puan = (
            0.6 * (rrf_puani / (2 / 61))
            + 0.4 * uyum
        )

        sonuclar.append(
            (
                final_puan,
                tarif,
                uyum,
                mevcut,
                eksik
            )
        )

    sonuclar.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return sonuclar


# ARAMA ISLEMI

if ara:

    malzemeler = [
        temizle(m.strip())
        for m in giris.split(",")
        if m.strip()
    ]

    if not malzemeler or not sorgu.strip():

        st.session_state.pop("sonuclar", None)

        st.warning(
            "Lütfen malzemelerini ve yemek tercihini gir."
        )

    else:

        with st.spinner(
            "Sana en uygun tarifler aranıyor..."
        ):

            st.session_state["sonuclar"] = tarif_ara(
                malzemeler,
                sorgu
            )[:sonuc_sayisi]


# TARIF KARTLARI

if "sonuclar" in st.session_state:

    sonuclar = st.session_state["sonuclar"]

    st.divider()

    st.header("✨ Sana Özel Tarif Önerileri")

    st.write(
        f"Senin için {len(sonuclar)} tarif seçtik."
    )

    if not sonuclar:

        st.info("Uygun tarif bulunamadı.")

    for sira, sonuc in enumerate(
        sonuclar, start=1
    ):

        puan, tarif, uyum, mevcut, eksik = sonuc

        with st.container(border=True):

            if sira == 1:
                st.success("⭐ En iyi eşleşme")

            st.subheader(
                f"{sira}. {tarif['title']}"
            )

            st.caption(
                "🍽️ Kategori: " +
                str(tarif.get("category") or "Belirtilmemiş")
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Malzeme Uyumu",
                f"%{uyum * 100:.0f}"
            )

            c2.metric(
                "Mevcut Malzeme",
                len(mevcut)
            )

            c3.metric(
                "Eksik Malzeme",
                len(eksik)
            )

            st.progress(float(uyum))

            sol, sag = st.columns(2)

            with sol:

                st.markdown(
                    "### ✅ Mutfağında Bulunanlar"
                )

                if mevcut:

                    for m in mevcut:
                        st.write("• " + m)

                else:

                    st.write(
                        "Eşleşen malzeme bulunamadı."
                    )

            with sag:

                st.markdown(
                    "### 🛒 Alışveriş Listesi"
                )

                if eksik:

                    for m in eksik:
                        st.write("• " + m)

                else:

                    st.success(
                        "Tüm malzeme isimleri eşleşti!"
                    )

            with st.expander(
                "📋 Tarifin Tüm Malzemeleri"
            ):

                for m in tarif.get("ingredients") or []:

                    st.write("• " + m)

            with st.expander(
                "👩‍🍳 Tarifin Hazırlanışı"
            ):

                adimlar = tarif.get(
                    "instructions"
                ) or []

                if isinstance(adimlar, list):

                    for no, adim in enumerate(
                        adimlar, start=1
                    ):

                        st.write(f"{no}. {adim}")

                elif adimlar:

                    st.write(adimlar)

                else:

                    st.info(
                        "Hazırlanış bilgisi bulunamadı."
                    )

            st.caption(
                f"Hibrit arama puanı: {puan:.3f}"
            )

            st.caption(
                "Malzeme uyumu isim eşleşmesine dayanır. "
                "Malzeme miktarları kontrol edilmemektedir."
            )


# ALT BILGI

st.divider()

st.markdown("""
<div class="footer">
    <strong>🍃 RecipeMind-AI</strong><br>
    Yapay Zekâ Destekli Akıllı Yemek Tarifi Sistemi
    <br><br>
    Daha az israf, daha akıllı tarifler.
</div>
""", unsafe_allow_html=True)