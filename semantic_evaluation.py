import json
import time
import faiss
import numpy as np

from pathlib import Path
from search_engine import sistemi_yukle, kelimeler

BASE = Path(__file__).resolve().parent

print("=" * 60)
print("RecipeMind AI - Anlamsal Arama Deneyi")
print("=" * 60)

tarifler, model, index, bm25 = sistemi_yukle()

K = 5

# TEST SORGULARI

testler = [

    {
        "id": 1,
        "sorgu": "Sabah tuketebilecegim pratik yiyecekler",
        "beklenen": "Kahvaltilik tarifler"
    },

    {
        "id": 2,
        "sorgu": "Et icermeyen doyurucu yemek",
        "beklenen": "Vejetaryen yemekler"
    },

    {
        "id": 3,
        "sorgu": "Serinletici yaz lezzetleri",
        "beklenen": "Soguk tatlilar ve icecekler"
    },

    {
        "id": 4,
        "sorgu": "Bayat ekmegi degerlendirmek istiyorum",
        "beklenen": "Bayat ekmek kullanilan tarifler"
    },

    {
        "id": 5,
        "sorgu": "Hafif bir aksam ogunu",
        "beklenen": "Hafif salata ve sebze yemekleri"
    },

    {
        "id": 6,
        "sorgu": "Hastayken icimi isitacak bir yemek",
        "beklenen": "Sicak corbalar"
    },

    {
        "id": 7,
        "sorgu": "Cayin yaninda ikram edilecek lezzetler",
        "beklenen": "Kek, kurabiye ve borek"
    },

    {
        "id": 8,
        "sorgu": "Dogum gununde ikram edilecek tatli",
        "beklenen": "Pasta ve kutlama tatlilari"
    },

    {
        "id": 9,
        "sorgu": "Spor sonrasi proteinli bir ogun",
        "beklenen": "Protein kaynaklari iceren yemekler"
    },

    {
        "id": 10,
        "sorgu": "Firina ihtiyac duymadan hazirlanan tatli",
        "beklenen": "Firinsiz tatlilar"
    }

]


# BM25 ARAMA

def bm25_ara(sorgu):

    puanlar = bm25.get_scores(
        kelimeler(sorgu)
    )

    return [

        int(i)

        for i in np.argsort(puanlar)[::-1]

        if puanlar[i] > 0

    ][:K]


# ANLAMSAL ARAMA

def anlamsal_ara(sorgu):

    vektor = np.array(

        model.encode([sorgu]),

        dtype="float32"

    )

    faiss.normalize_L2(vektor)

    _, indeksler = index.search(vektor, K)

    return [

        int(i)

        for i in indeksler[0]

        if i >= 0

    ]


# MODELI ISINDIR

model.encode(["deneme sorgusu"])

tum_sonuclar = []

# DENEYLER

for test in testler:

    print("\n" + "=" * 60)

    print("Sorgu:", test["sorgu"])

    print("Beklenen:", test["beklenen"])

    yontemler = [

        ("BM25", bm25_ara),

        ("Semantic Search", anlamsal_ara)

    ]

    for yontem, fonksiyon in yontemler:

        baslangic = time.perf_counter()

        indeksler = fonksiyon(test["sorgu"])

        sure = (
            time.perf_counter() - baslangic
        ) * 1000

        print("\nYontem:", yontem)

        print("Arama suresi:", round(sure, 2), "ms")

        for sira, i in enumerate(indeksler, 1):

            tarif = tarifler[i]

            print(
                sira,
                "-",
                tarif.get("title", "")
            )

            tum_sonuclar.append({

                "test_id": test["id"],

                "sorgu": test["sorgu"],

                "beklenen": test["beklenen"],

                "yontem": yontem,

                "sira": sira,

                "tarif_id": i,

                "tarif_adi": tarif.get("title", ""),

                "kategori": tarif.get("category", ""),

                "malzemeler": tarif.get("ingredients", []),

                "hazirlama_suresi": tarif.get("prep_time", ""),

                "talimatlar": tarif.get("instructions", []),

                "arama_suresi_ms": sure

            })


# SONUCLARI KAYDET

with open(

    BASE / "semantic_evaluation_results.json",

    "w",

    encoding="utf-8"

) as dosya:

    json.dump(

        tum_sonuclar,

        dosya,

        ensure_ascii=False,

        indent=4

    )

print("\n" + "=" * 60)

print("Anlamsal arama deneyleri tamamlandi.")

print("Toplam sonuc kaydi:", len(tum_sonuclar))

print("Sonuclar semantic_evaluation_results.json dosyasina kaydedildi.")