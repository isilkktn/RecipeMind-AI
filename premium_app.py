import streamlit as st
import base64
import time
import re
import html

from pathlib import Path
from PIL import Image, ImageOps
from search_engine import sistemi_yukle, tarif_ara


# SAYFA AYARLARI

st.set_page_config(
    page_title="RecipeMind AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE = Path(__file__).resolve().parent


# ARAMA MOTORU

@st.cache_resource
def motoru_yukle():
    return sistemi_yukle()


# OTURUM BILGILERI

if "favoriler" not in st.session_state:
    st.session_state.favoriler = {}

if "alisveris" not in st.session_state:
    st.session_state.alisveris = []

if "sonuclar" not in st.session_state:
    st.session_state.sonuclar = []


# ANA SAYFA FOTOGRAFI

foto = BASE / "assets" / "hero.jpg"

with open(foto, "rb") as dosya:
    gorsel = base64.b64encode(
        dosya.read()
    ).decode()


# TASARIM

st.html("""
<style>

.stApp {
    background: #FAF8F3;
    color: #283C30;
}

[data-testid="stHeader"] {
    background: #FAF8F3;
}

.block-container {
    max-width: 1300px;
    padding-top: 3rem;
}

h1, h2, h3, h4 {
    font-family: Georgia, serif;
    color: #243D30 !important;
}

.brand {
    font-family: Georgia, serif;
    font-size: 34px;
    font-weight: bold;
    color: #243D30;
}

.brand span {
    color: #B8754D;
}

.tagline {
    color: #68776B;
    font-size: 12px;
    letter-spacing: 2px;
}

[data-testid="stTabs"] [role="tablist"] {
    gap: 15px;
    border-bottom: 1px solid #DCE2D6;
}

[data-testid="stTabs"] button {
    padding: 12px 20px;
}

[data-testid="stTabs"] button p {
    font-size: 15px;
    font-weight: 600;
    color: #38583F;
}

.hero {
    display: flex;
    align-items: center;
    background: #EEEDE3;
    border-radius: 28px;
    overflow: hidden;
    min-height: 340px;
    margin-top: 20px;
    margin-bottom: 25px;
}

.hero-content {
    width: 52%;
    padding: 38px;
    box-sizing: border-box;
}

.hero-content h1 {
    font-size: clamp(30px, 4vw, 52px);
    line-height: 1.15;
    margin-top: 15px;
    margin-bottom: 20px;
}

.hero-content p {
    color: #526457;
    font-size: 17px;
    line-height: 1.7;
}

.hero-image {
    width: 48%;
    min-height: 340px;
    background-size: cover;
    background-position: center;
    align-self: stretch;
}

.eyebrow {
    display: inline-block;
    background: #DCE5D5;
    color: #38583F;
    padding: 8px 16px;
    border-radius: 30px;
    font-size: 12px;
    letter-spacing: 1px;
}

.section-title {
    font-family: Georgia, serif;
    color: #243D30;
    font-size: 32px;
    margin-bottom: 8px;
}

.stTextInput input {
    background: white !important;
    color: #243D30 !important;
    padding: 14px;
}

[data-baseweb="input"],
[data-baseweb="select"] > div {
    background: white !important;
    color: #243D30 !important;
    border-radius: 12px;
}

.stFormSubmitButton > button {
    background: #38583F !important;
    color: white !important;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 600;
}

.stFormSubmitButton > button:hover {
    background: #B8754D !important;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    border: 1px solid #DCE2D6;
    background: #FFFFFF;
    color: #38583F;
}

.stButton > button:hover {
    border-color: #38583F;
    color: #38583F;
    background: #E8EFE5;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 18px;
    box-shadow: 0 5px 18px #243D3010;
}

[data-testid="stExpander"] {
    background: #FAF8F3;
    border-radius: 10px;
}

[data-testid="stImage"] img {
    border-radius: 14px;
    object-fit: cover;
}

.recipe-banner {
    border-radius: 16px;
    padding: 25px;
    background: linear-gradient(
        135deg, #DCE5D5, #F0EBDD
    );
    text-align: center;
}

.recipe-icon {
    font-size: 50px;
}

.recipe-category {
    color: #38583F;
    font-size: 13px;
    font-weight: 600;
}

.recipe-title {
    font-family: Georgia, serif;
    color: #243D30;
    font-size: 23px;
    font-weight: bold;
    min-height: 64px;
}

.match-label {
    font-size: 13px;
    color: #526457;
    margin-top: 8px;
}

.match-value {
    font-family: Georgia, serif;
    font-size: 34px;
    font-weight: bold;
}

.match-track {
    background: #E7EAE2;
    height: 9px;
    border-radius: 15px;
    overflow: hidden;
    margin: 10px 0;
}

.ingredient-tag {
    display: inline-block;
    border-radius: 20px;
    font-size: 12px;
    padding: 6px 10px;
    margin: 3px;
}

.available {
    background: #E1EDDF;
    color: #345B39;
}

.missing {
    background: #F6E4D6;
    color: #8C4928;
}

.feature {
    background: white;
    border: 1px solid #E5E7DE;
    border-radius: 18px;
    padding: 24px;
    min-height: 180px;
    box-shadow: 0 6px 18px #243D3008;
}

.feature h3 {
    font-size: 23px;
}

.feature p {
    color: #68776B;
    font-size: 14px;
}

.feature-icon {
    font-size: 32px;
}

.footer {
    text-align: center;
    color: #68776B;
    font-size: 14px;
    padding: 25px;
}

@media (max-width: 700px) {

    .hero {
        flex-direction: column;
    }

    .hero-content,
    .hero-image {
        width: 100%;
    }

    .hero-content {
        padding: 25px;
    }

    .hero-image {
        min-height: 220px;
    }
}

</style>
""")


# KATEGORI FOTOGRAFLARI

def kategori_fotografi(kategori):

    kategori = str(kategori).replace(
        "I", "ı"
    ).replace("İ", "i").lower()

    if "kahvalt" in kategori:
        dosya = "breakfast.jpg"

    elif "tatlı" in kategori:
        dosya = "dessert.jpg"

    elif "çorba" in kategori:
        dosya = "soup.jpg"

    elif "salata" in kategori:
        dosya = "salad.jpg"

    elif "makarna" in kategori:
        dosya = "pasta.jpg"

    elif "börek" in kategori:
        dosya = "pastry.jpg"

    elif "et yemek" in kategori:
        dosya = "meat.jpg"

    else:
        dosya = "default.jpg"

    return BASE / "assets" / "recipes" / dosya


# FOTOGRAFLARI ESIT BOYUTLANDIRMA

@st.cache_data
def fotograf_hazirla(dosya):

    with Image.open(dosya) as resim:

        resim = ImageOps.exif_transpose(resim)

        resim = resim.convert("RGB")

        resim = ImageOps.fit(
            resim,
            (800, 480),
            method=Image.Resampling.LANCZOS
        )

        return resim


# KATEGORI SIMGELERI

def kategori_simgesi(kategori):

    kategori = str(kategori).lower()

    if "kahvalt" in kategori:
        return "🍳"

    if "tatlı" in kategori:
        return "🍰"

    if "çorba" in kategori:
        return "🥣"

    if "salata" in kategori:
        return "🥗"

    if "makarna" in kategori:
        return "🍝"

    if "börek" in kategori:
        return "🥐"

    if "et yemek" in kategori:
        return "🍖"

    return "🍽️"


# SURE HESAPLAMA

def sure_hesapla(deger):

    if isinstance(deger, (int, float)):
        return int(deger) if deger >= 0 else None

    metin = str(deger or "").strip().upper()

    if metin.isdigit():
        return int(metin)

    iso = re.fullmatch(
        r"PT(?:(\d+)H)?(?:(\d+)M)?",
        metin
    )

    if iso:

        saat = int(iso.group(1) or 0)
        dakika = int(iso.group(2) or 0)

        return saat * 60 + dakika

    saat = re.search(
        r"(\d+)\s*SAAT",
        metin
    )

    dakika = re.search(
        r"(\d+)\s*(DK|DAKİKA|DAKIKA)",
        metin
    )

    if saat or dakika:

        return (
            int(saat.group(1)) * 60 if saat else 0
        ) + (
            int(dakika.group(1)) if dakika else 0
        )

    return None


# TARIF KARTLARI

def tarif_karti(sonuc, alan):

    tarif = sonuc["tarif"]
    tarif_id = sonuc["id"]
    uyum = sonuc["uyum"]

    kategori = str(
        tarif.get("category") or "Yemek Tarifi"
    )

    baslik = html.escape(
        str(tarif.get("title") or "Yemek Tarifi")
    )

    simge = kategori_simgesi(kategori)

    yuzde = round(uyum * 100)

    if yuzde >= 75:
        renk = "#527A46"

    elif yuzde >= 40:
        renk = "#B8754D"

    else:
        renk = "#B4554A"

    with st.container(border=True):

        fotograf = kategori_fotografi(kategori)

        if not fotograf.exists():

            fotograf = (
                BASE / "assets" / "recipes" / "default.jpg"
            )

        fotograf_gosterildi = False

        if fotograf.exists():

            try:

                resim = fotograf_hazirla(
                    str(fotograf)
                )

                st.image(
                    resim,
                    use_container_width=True
                )

                st.caption(
                    "Temsili kategori görseli"
                )

                fotograf_gosterildi = True

            except Exception:

                fotograf_gosterildi = False

        if not fotograf_gosterildi:

            st.html(f"""
            <div class="recipe-banner">
            <div class="recipe-icon">{simge}</div>
            </div>
            """)

        st.html(f"""
        <div class="recipe-category">
        {html.escape(kategori)}
        </div>
        """)

        st.html(f"""
        <div class="recipe-title">
        {baslik}
        </div>
        """)

        sure = sure_hesapla(
            tarif.get("prep_time")
        )

        if sure is not None:

            st.caption(
                f"⏱️ Hazırlama: {sure} dakika"
            )

        else:

            st.caption(
                "⏱️ Hazırlama süresi belirtilmemiş"
            )

        st.html(f"""
        <div class="match-label">
        MALZEME UYUMU
        </div>

        <div class="match-value"
        style="color:{renk}">
        %{yuzde}
        </div>

        <div class="match-track">
        <div style="width:{yuzde}%;
        background:{renk};
        height:9px;">
        </div>
        </div>
        """)

        st.write(
            f"✅ {len(sonuc['mevcut'])} eşleşen malzeme"
        )

        st.write(
            f"🛒 {len(sonuc['eksik'])} eksik malzeme"
        )

        if uyum == 1:

            st.success(
                "Tüm malzeme isimleri eşleşti!"
            )

        favori = (
            tarif_id in st.session_state.favoriler
        )

        if st.button(

            "❤️ Favoriden Çıkar"
            if favori
            else "🤍 Favorilere Ekle",

            key=f"{alan}_favori_{tarif_id}",

            use_container_width=True

        ):

            if favori:

                del st.session_state.favoriler[
                    tarif_id
                ]

            else:

                st.session_state.favoriler[
                    tarif_id
                ] = sonuc

            st.rerun()

        with st.expander("Tarifi İncele"):

            st.markdown(
                "**Mutfağında Bulunanlar**"
            )

            if sonuc["mevcut"]:

                etiketler = "".join(

                    '<span class="ingredient-tag available">'
                    + html.escape(str(m))
                    + '</span>'

                    for m in sonuc["mevcut"]
                )

                st.html(etiketler)

            else:

                st.write(
                    "Eşleşen malzeme bulunamadı."
                )

            st.markdown(
                "**Eksik Malzemeler**"
            )

            if sonuc["eksik"]:

                etiketler = "".join(

                    '<span class="ingredient-tag missing">'
                    + html.escape(str(m))
                    + '</span>'

                    for m in sonuc["eksik"]
                )

                st.html(etiketler)

                if st.button(

                    "🛒 Alışveriş Listesine Ekle",

                    key=f"{alan}_liste_{tarif_id}",

                    use_container_width=True

                ):

                    for m in sonuc["eksik"]:

                        if m not in st.session_state.alisveris:

                            st.session_state.alisveris.append(m)

                    st.rerun()

            else:

                st.write(
                    "Eksik malzeme bulunamadı."
                )

            st.markdown("**Tüm Malzemeler**")

            for m in tarif.get("ingredients") or []:

                st.write("• " + str(m))

            st.markdown("**Hazırlanışı**")

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

            st.markdown("**Neden Bu Tarif?**")

            st.write(
                f"Bu tarif, yemek tercihin ve "
                f"malzeme eşleşmen dikkate alınarak "
                f"önerildi. Tarifin malzemelerinin "
                f"%{yuzde} kadarı isim olarak eşleşiyor."
            )

            st.caption(
                "Kural tabanlı öneri açıklaması."
            )

            st.caption(
                f"Hibrit arama puanı: "
                f"{sonuc['puan']:.3f}"
            )


# KARTLARI YAN YANA GOSTER

def kartlari_goster(sonuclar, alan):

    for baslangic in range(
        0, len(sonuclar), 3
    ):

        kolonlar = st.columns(3)

        for j, sonuc in enumerate(
            sonuclar[baslangic:baslangic + 3]
        ):

            with kolonlar[j]:

                tarif_karti(sonuc, alan)


# LOGO

st.html("""
<div class="brand">
🌿 RecipeMind<span> AI</span>
</div>

<div class="tagline">
AKILLI MUTFAK • SÜRDÜRÜLEBİLİR YAŞAM
</div>
""")


# UST NAVIGASYON MENUSU

kesfet, favoriler, alisveris, analiz = st.tabs([

    "🏠 Tarif Keşfet",

    f"❤️ Favorilerim ({len(st.session_state.favoriler)})",

    f"🛒 Alışveriş Listem ({len(st.session_state.alisveris)})",

    "📊 Sistem Analizi"

])


# TARIF KESFET SAYFASI

with kesfet:

    st.html(f"""
    <div class="hero">

    <div class="hero-content">

    <span class="eyebrow">
    YAPAY ZEKÂ DESTEKLİ MUTFAK
    </span>

    <h1>Lezzet, mutfağında<br>başlar.</h1>

    <p>
    Elindeki malzemelerle harikalar yarat.
    Yapay zekâ ile sana özel tarifler keşfet,
    yeni lezzetler dene ve gıda israfını azalt.
    </p>

    </div>

    <div class="hero-image"
    style="background-image:
    url('data:image/jpeg;base64,{gorsel}');">
    </div>

    </div>
    """)

    st.html("""
    <div class="section-title">
    Bugün ne pişiriyoruz?
    </div>
    """)

    st.caption(
        "Mutfağındaki malzemeleri söyle, "
        "sana uygun lezzetleri keşfedelim."
    )

    with st.form("tarif_arama"):

        sol, sag = st.columns(2)

        malzemeler = sol.text_input(
            "🥑 Evindeki malzemeler",
            placeholder="Domates, yumurta, peynir..."
        )

        tercih = sag.text_input(
            "🍽️ Canın ne çekiyor?",
            placeholder="Hafif ve pratik bir yemek..."
        )

        c1, c2, c3 = st.columns(3)

        kategori = c1.selectbox(

            "Yemek kategorisi",

            [
                "Tümü",
                "Kahvaltı",
                "Ana Yemek",
                "Çorba",
                "Salata",
                "Tatlı",
                "Börek",
                "Makarna"
            ]
        )

        sure_secimi = c2.selectbox(

            "Hazırlama süresi",

            [
                "Fark etmez",
                "15 dakika",
                "30 dakika",
                "60 dakika"
            ]
        )

        siralama = c3.selectbox(

            "Sıralama",

            [
                "En uygun tarifler",
                "En yüksek malzeme uyumu",
                "En az eksik malzeme"
            ]
        )

        ara = st.form_submit_button(
            "Tarifleri Keşfet →",
            use_container_width=True
        )

    if ara:

        st.session_state.sonuclar = []

        if not malzemeler.strip() or not tercih.strip():

            st.warning(
                "Lütfen iki alanı da doldur."
            )

        else:

            with st.spinner(
                "Sana özel tarifler hazırlanıyor..."
            ):

                try:

                    sistem = motoru_yukle()

                    baslangic = time.perf_counter()

                    sonuclar = tarif_ara(
                        sistem,
                        malzemeler,
                        tercih,
                        adet=200
                    )

                    if kategori != "Tümü":

                        kategori_anahtari = (
                            kategori.lower()[:5]
                        )

                        sonuclar = [

                            s for s in sonuclar

                            if kategori_anahtari in str(
                                s["tarif"].get("category") or ""
                            ).lower()

                        ]

                    if sure_secimi != "Fark etmez":

                        maksimum = int(
                            sure_secimi.split()[0]
                        )

                        filtrelenen = []

                        for s in sonuclar:

                            sure = sure_hesapla(
                                s["tarif"].get("prep_time")
                            )

                            if sure is not None and sure <= maksimum:

                                filtrelenen.append(s)

                        sonuclar = filtrelenen

                    if siralama == "En yüksek malzeme uyumu":

                        sonuclar.sort(
                            key=lambda s: s["uyum"],
                            reverse=True
                        )

                    elif siralama == "En az eksik malzeme":

                        sonuclar.sort(
                            key=lambda s: len(s["eksik"])
                        )

                    st.session_state.sonuclar = sonuclar[:6]

                    st.session_state.arama_suresi = (
                        time.perf_counter() - baslangic
                    )

                    if not sonuclar:

                        st.info(
                            "Arama sonuçlarında filtrelerine "
                            "uygun tarif bulunamadı."
                        )

                except Exception as hata:

                    st.error(
                        f"Arama hatası: {hata}"
                    )

                    st.exception(hata)

    if st.session_state.sonuclar:

        st.divider()

        st.html("""
        <div class="section-title">
        Sana özel lezzetler
        </div>
        """)

        st.caption(
            f"{len(st.session_state.sonuclar)} tarif "
            f"• Arama süresi: "
            f"{st.session_state.get('arama_suresi', 0):.3f} saniye"
        )

        kartlari_goster(
            st.session_state.sonuclar,
            "arama"
        )

        st.caption(
            "Malzeme uyumu isim eşleşmesine dayanır. "
            "Malzeme miktarları kontrol edilmez. "
            "Yemek fotoğrafları temsilidir."
        )

    st.divider()

    st.html("""
    <div class="section-title">
    Akıllı mutfağın avantajları
    </div>
    """)

    c1, c2, c3 = st.columns(3)

    with c1:

        st.html("""
        <div class="feature">
        <div class="feature-icon">🥗</div>
        <h3>Sana Özel Tarifler</h3>
        <p>
        Malzemelerine ve yemek tercihlerine
        uygun akıllı öneriler.
        </p>
        </div>
        """)

    with c2:

        st.html("""
        <div class="feature">
        <div class="feature-icon">🌱</div>
        <h3>Daha Az İsraf</h3>
        <p>
        Evindeki malzemeleri değerlendir,
        sürdürülebilir bir mutfak oluştur.
        </p>
        </div>
        """)

    with c3:

        st.html("""
        <div class="feature">
        <div class="feature-icon">✨</div>
        <h3>Akıllı Teknoloji</h3>
        <p>
        Anlamsal arama ve hibrit bilgi erişimi
        ile yeni lezzetler keşfet.
        </p>
        </div>
        """)


# FAVORILER SAYFASI

with favoriler:

    st.title("Sevdiğin lezzetler")

    st.write(
        "Favori tariflerinin tamamı bir arada."
    )

    if not st.session_state.favoriler:

        st.info(
            "Henüz favori tarifin yok. "
            "Tarif kartlarındaki kalp butonuna bas."
        )

    else:

        kartlari_goster(

            list(
                st.session_state.favoriler.values()
            ),

            "favori"
        )


# ALISVERIS LISTESI SAYFASI

with alisveris:

    st.title("Alışveriş Listem")

    st.write(
        "Bir sonraki alışverişinde ihtiyacın "
        "olan malzemeler."
    )

    if not st.session_state.alisveris:

        st.info(
            "Alışveriş listen henüz boş."
        )

    else:

        secilenler = []

        for m in st.session_state.alisveris:

            if st.checkbox(

                str(m),

                key=f"alisveris_{m}"

            ):

                secilenler.append(m)

        c1, c2, c3 = st.columns(3)

        if c1.button("Seçilenleri Kaldır"):

            st.session_state.alisveris = [

                m for m in st.session_state.alisveris

                if m not in secilenler

            ]

            st.rerun()

        c2.download_button(

            "📥 Listeyi İndir",

            data="\n".join(
                map(str, st.session_state.alisveris)
            ),

            file_name="alisveris_listem.txt",

            mime="text/plain"
        )

        if c3.button("Listeyi Temizle"):

            st.session_state.alisveris = []

            st.rerun()


# SISTEM ANALIZI SAYFASI

with analiz:

    st.title("Bilgi Erişim Sistemi")

    st.write(
        "RecipeMind-AI arama motorunun "
        "teknik mimarisi ve çalışma prensibi."
    )

    st.header("Kullanılan Teknolojiler")

    st.table([

        {
            "Teknoloji": "BM25",
            "Görevi": "Kelime tabanlı arama"
        },

        {
            "Teknoloji": "Sentence Transformers",
            "Görevi": "Anlamsal arama"
        },

        {
            "Teknoloji": "FAISS",
            "Görevi": "Vektör benzerlik araması"
        },

        {
            "Teknoloji": "RRF",
            "Görevi": "Arama sıralamalarını birleştirme"
        },

        {
            "Teknoloji": "Ingredient Matching",
            "Görevi": "Malzeme eşleştirme"
        },

        {
            "Teknoloji": "Streamlit",
            "Görevi": "Web arayüzü"
        }

    ])

    st.header("Sistem Mimarisi")

    st.code("""
Kullanıcı Sorgusu
        |
        v
BM25 + Anlamsal Arama (FAISS)
        |
        v
Reciprocal Rank Fusion (RRF)
        |
        v
Malzeme Eşleştirme
        |
        v
Hibrit Puanlama
        |
        v
Kişiselleştirilmiş Tarif Önerileri
    """, language="text")

    st.header("Hibrit Arama Ağırlıkları")

    st.bar_chart({

        "Ağırlık (%)": {

            "RRF": 60,

            "Malzeme Uyumu": 40

        }

    })

    st.caption(
        "Bu değerler algoritma ağırlıklarıdır. "
        "Doğruluk veya başarı oranı değildir."
    )

    if "arama_suresi" in st.session_state:

        st.metric(

            "Son Arama Süresi",

            f"{st.session_state.arama_suresi:.3f} saniye"
        )

    if st.button("Veri Seti Bilgilerini Göster"):

        try:

            sistem = motoru_yukle()

            tarifler, model, index, bm25 = sistem

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Toplam Tarif",
                len(tarifler)
            )

            c2.metric(
                "Vektör Boyutu",
                index.d
            )

            c3.metric(
                "İndekslenen Tarif",
                index.ntotal
            )

        except Exception as hata:

            st.error(str(hata))

    st.info(
        "Precision@K, Recall@K ve nDCG "
        "değerlendirmeleri henüz yapılmadı."
    )


# ALT BILGI

st.divider()

st.html("""
<div class="footer">

<strong>🌿 RecipeMind AI</strong>

<br><br>

İyi yemek. Akıllı seçimler. Daha az israf.

<br><br>

© 2026 RecipeMind-AI

</div>
""")