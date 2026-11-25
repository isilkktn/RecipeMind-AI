import streamlit as st
import base64
from pathlib import Path

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


# ANA SAYFA FOTOGRAFI

foto = BASE / "assets" / "hero.jpg"

with open(foto, "rb") as dosya:
    gorsel = base64.b64encode(
        dosya.read()
    ).decode()


# TASARIM AYARLARI

st.html("""
<style>

.stApp {
    background-color: #FAF8F3;
    color: #283C30;
}

[data-testid="stHeader"] {
    background-color: #FAF8F3;
}

.block-container {
    max-width: 1300px;
    padding-top: 3rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    font-family: Georgia, serif;
    color: #243D30 !important;
}

.brand {
    font-family: Georgia, serif;
    font-size: 32px;
    font-weight: bold;
    color: #243D30;
}

.brand span {
    color: #C17A50;
}

.tagline {
    color: #68776B;
    font-size: 13px;
    letter-spacing: 2px;
}

.hero {
    display: flex;
    align-items: center;
    background: #EEEDE3;
    border-radius: 28px;
    overflow: hidden;
    min-height: 360px;
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
    min-height: 360px;
    background-size: cover;
    background-position: center;
    align-self: stretch;
}

.badge {
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

[data-baseweb="input"] {
    background: white !important;
    border-radius: 12px;
    border-color: #D6DCCF;
}

[data-testid="stWidgetLabel"] p {
    color: #243D30 !important;
    font-weight: 600;
}

.stFormSubmitButton > button {
    background: #38583F !important;
    color: white !important;
    border: none;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stFormSubmitButton > button:hover {
    background: #C17A50 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 18px;
}

[data-testid="stExpander"] {
    background: #FAF8F3;
    border-radius: 10px;
}

[data-testid="stProgress"] > div > div > div {
    background-color: #66885E;
}

.feature {
    background: white;
    border: 1px solid #E5E7DE;
    border-radius: 18px;
    padding: 24px;
    min-height: 190px;
    box-shadow: 0 6px 18px #243D3008;
    transition: all 0.2s ease;
}

.feature:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 25px #243D3015;
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
    margin-bottom: 12px;
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


# LOGO

st.html("""
<div class="brand">
🌿 RecipeMind<span> AI</span>
</div>

<div class="tagline">
AKILLI MUTFAK • SÜRDÜRÜLEBİLİR YAŞAM
</div>
""")


# ANA SAYFA GORSELI

st.html(f"""
<div class="hero">
<div class="hero-content">

<span class="badge">
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
style="background-image: url('data:image/jpeg;base64,{gorsel}');">
</div>

</div>
""")


# ARAMA PANELI

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

    ara = st.form_submit_button(
        "Tarifleri Keşfet →",
        use_container_width=True
    )


# ARAMA ISLEMI

if ara:

    st.session_state["sonuclar"] = []

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

                sonuclar = tarif_ara(
                    sistem,
                    malzemeler,
                    tercih,
                    adet=6
                )

                st.session_state["sonuclar"] = sonuclar

                if sonuclar:

                    st.success(
                        f"Senin için {len(sonuclar)} tarif bulundu!"
                    )

                else:

                    st.warning(
                        "Uygun tarif bulunamadı."
                    )

            except Exception as hata:

                st.error(
                    f"Arama sırasında hata oluştu: {hata}"
                )

                st.exception(hata)


# TARIF SONUCLARI

if st.session_state.get("sonuclar"):

    st.divider()

    st.html("""
    <div class="section-title">
    Sana özel lezzetler
    </div>
    """)

    st.caption(
        "Mutfağındaki malzemelere ve tercihlerine "
        "göre seçilen tarifler."
    )

    sonuclar = st.session_state["sonuclar"]

    for baslangic in range(0, len(sonuclar), 3):

        kolonlar = st.columns(3)

        for j, sonuc in enumerate(
            sonuclar[baslangic:baslangic + 3]
        ):

            tarif = sonuc["tarif"]

            uyum = sonuc["uyum"]

            with kolonlar[j]:

                with st.container(border=True):

                    if baslangic == 0 and j == 0:

                        st.caption("⭐ EN İYİ EŞLEŞME")

                    st.subheader(
                        tarif.get("title") or "Yemek Tarifi"
                    )

                    st.caption(
                        "🍽️ " + str(
                            tarif.get("category")
                            or "Yemek Tarifi"
                        )
                    )

                    st.metric(
                        "Malzeme Uyumu",
                        f"%{uyum * 100:.0f}"
                    )

                    st.progress(float(uyum))

                    st.write(
                        f"✅ {len(sonuc['mevcut'])} "
                        "eşleşen malzeme"
                    )

                    st.write(
                        f"🛒 {len(sonuc['eksik'])} "
                        "eksik malzeme"
                    )

                    with st.expander(
                        "🥑 Malzemeleri İncele"
                    ):

                        st.markdown(
                            "**Mutfağında bulunanlar**"
                        )

                        if sonuc["mevcut"]:

                            for m in sonuc["mevcut"]:

                                st.write("✅ " + str(m))

                        else:

                            st.write(
                                "Eşleşen malzeme bulunamadı."
                            )

                        st.markdown(
                            "**Eksik malzemeler**"
                        )

                        if sonuc["eksik"]:

                            for m in sonuc["eksik"]:

                                st.write("🛒 " + str(m))

                        else:

                            st.success(
                                "Tüm malzeme isimleri eşleşti!"
                            )

                    with st.expander(
                        "📋 Tüm Malzemeler"
                    ):

                        for m in tarif.get("ingredients") or []:

                            st.write("• " + str(m))

                    with st.expander(
                        "👩‍🍳 Tarifi Gör"
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

                    with st.expander(
                        "✨ Neden Bu Tarif?"
                    ):

                        st.write(
                            f"Bu tarif, yemek tercihin ve "
                            f"malzeme eşleşmen dikkate "
                            f"alınarak önerildi. Tarifin "
                            f"malzemelerinin "
                            f"%{uyum * 100:.0f} kadarı "
                            f"elindeki malzemelerle eşleşiyor."
                        )

                        st.caption(
                            "Kural tabanlı öneri açıklaması."
                        )

                    st.caption(
                        f"Hibrit arama puanı: "
                        f"{sonuc['puan']:.3f}"
                    )

    st.caption(
        "Malzeme uyumu isim eşleşmesine dayanır. "
        "Malzeme miktarları kontrol edilmez."
    )


# OZELLIK KARTLARI

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