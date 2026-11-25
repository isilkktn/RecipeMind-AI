import json
import time
import numpy as np
import faiss

from pathlib import Path
from search_engine import (
    sistemi_yukle,
    tarif_ara,
    kelimeler
)

BASE = Path(__file__).resolve().parent

# TEST SORGULARI

test_sorgulari = [
    {
        "id": 1,
        "malzemeler": "patates, yumurta, peynir, tuz",
        "sorgu": "Kolay ve pratik bir kahvaltı"
    },
    {
        "id": 2,
        "malzemeler": "tavuk, domates, biber, soğan",
        "sorgu": "Tavuklu akşam yemeği"
    },
    {
        "id": 3,
        "malzemeler": "mercimek, soğan, havuç, patates",
        "sorgu": "Mercimek çorbası"
    },
    {
        "id": 4,
        "malzemeler": "süt, un, şeker, kakao",
        "sorgu": "Kolay çikolatalı tatlı"
    },
    {
        "id": 5,
        "malzemeler": "domates, salatalık, marul, limon",
        "sorgu": "Hafif sebzeli salata"
    },
    {
        "id": 6,
        "malzemeler": "makarna, domates, sarımsak",
        "sorgu": "Domates soslu makarna"
    },
    {
        "id": 7,
        "malzemeler": "un, yumurta, süt, peynir",
        "sorgu": "Peynirli hamur işi"
    },
    {
        "id": 8,
        "malzemeler": "patates, havuç, kabak, soğan",
        "sorgu": "Etsiz sebze yemeği"
    },
    {
        "id": 9,
        "malzemeler": "kıyma, soğan, ekmek, yumurta",
        "sorgu": "Ev yapımı köfte"
    },
    {
        "id": 10,
        "malzemeler": "pirinç, süt, şeker",
        "sorgu": "Sütlü tatlı"
    }
]

# SISTEMI YUKLE

print("RecipeMind AI - Performans Degerlendirmesi")
print("Arama sistemi yukleniyor...")

sistem = sistemi_yukle()

tarifler, model, index, bm25 = sistem

print("Toplam tarif:", len(tarifler))

K = 5

tum_sonuclar = []

# ALGORITMALARI TEST ET

for test in test_sorgulari:

    sorgu = test["sorgu"]
    malzemeler = test["malzemeler"]

    print("\n" + "=" * 60)
    print("Test:", test["id"])
    print("Sorgu:", sorgu)

    # BM25

    baslangic = time.perf_counter()

    bm25_puanlari = bm25.get_scores(
        kelimeler(sorgu)
    )

    bm25_siralama = [
        int(i)
        for i in np.argsort(bm25_puanlari)[::-1]
        if bm25_puanlari[i] > 0
    ][:100]

    bm25_sure = (
        time.perf_counter() - baslangic
    )

    # ANLAMSAL ARAMA

    baslangic = time.perf_counter()

    sorgu_vektoru = np.array(
        model.encode([sorgu]),
        dtype="float32"
    )

    faiss.normalize_L2(sorgu_vektoru)

    _, indeksler = index.search(
        sorgu_vektoru,
        100
    )

    semantic_siralama = [
        int(i)
        for i in indeksler[0]
        if i >= 0
    ]

    semantic_sure = (
        time.perf_counter() - baslangic
    )

    # RRF

    baslangic = time.perf_counter()

    rrf_puanlari = {}

    for siralama in [
        bm25_siralama,
        semantic_siralama
    ]:

        for sira, i in enumerate(
            siralama,
            start=1
        ):

            rrf_puanlari[i] = (
                rrf_puanlari.get(i, 0)
                + 1 / (60 + sira)
            )

    rrf_siralama = sorted(
        rrf_puanlari,
        key=rrf_puanlari.get,
        reverse=True
    )

    rrf_sure = (
        bm25_sure
        + semantic_sure
        + time.perf_counter()
        - baslangic
    )

    # RECIPEMIND HYBRIT

    baslangic = time.perf_counter()

    hibrit_sonuclar = tarif_ara(
        sistem,
        malzemeler,
        sorgu,
        adet=K
    )

    hibrit_siralama = [
        int(s["id"])
        for s in hibrit_sonuclar
    ]

    hibrit_sure = (
        time.perf_counter() - baslangic
    )

    # SONUCLARI BIRLESTIR

    yontemler = {
        "BM25": {
            "sonuclar": bm25_siralama[:K],
            "sure": bm25_sure
        },
        "Semantic Search": {
            "sonuclar": semantic_siralama[:K],
            "sure": semantic_sure
        },
        "RRF": {
            "sonuclar": rrf_siralama[:K],
            "sure": rrf_sure
        },
        "RecipeMind Hybrid": {
            "sonuclar": hibrit_siralama[:K],
            "sure": hibrit_sure
        }
    }

    for yontem, bilgi in yontemler.items():

        print("\nYontem:", yontem)

        print(
            "Arama suresi:",
            round(bilgi["sure"], 4),
            "saniye"
        )

        for sira, tarif_id in enumerate(
            bilgi["sonuclar"],
            start=1
        ):

            tarif = tarifler[tarif_id]

            print(
                sira,
                "-",
                tarif.get("title")
            )

            tum_sonuclar.append({
                "test_id": test["id"],
                "sorgu": sorgu,
                "malzemeler": malzemeler,
                "yontem": yontem,
                "sira": sira,
                "tarif_id": tarif_id,
                "tarif_adi": tarif.get("title"),
                "kategori": tarif.get("category"),
                "tarif_malzemeleri": tarif.get("ingredients"),
                "hazirlama_suresi": tarif.get("prep_time"),
                "arama_suresi": bilgi["sure"]
            })

# SONUCLARI DOSYAYA KAYDET

with open(
    BASE / "evaluation_results.json",
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
print("Testler tamamlandi.")
print("Sonuclar evaluation_results.json dosyasina kaydedildi.")