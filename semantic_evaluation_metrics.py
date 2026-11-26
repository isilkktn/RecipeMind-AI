import json
import math
import statistics

from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent

K = 5

# Arama sonuclarini yukle

with open(
    BASE / "semantic_evaluation_results.json",
    encoding="utf-8"
) as dosya:
    sonuclar = json.load(dosya)

# Ilgililik etiketlerini yukle

with open(
    BASE / "semantic_relevance_labels.json",
    encoding="utf-8"
) as dosya:
    etiketler = json.load(dosya)

havuz = defaultdict(dict)
gruplar = defaultdict(list)

for kayit in sonuclar:

    test_id = kayit["test_id"]
    tarif_id = kayit["tarif_id"]

    anahtar = f"{test_id}_{tarif_id}"

    if anahtar not in etiketler:
        raise ValueError(
            f"Eksik etiket: {anahtar}"
        )

    puan = etiketler[anahtar]

    if puan not in [0, 1, 2]:
        raise ValueError(
            f"Gecersiz etiket: {anahtar}"
        )

    havuz[test_id][tarif_id] = puan

    gruplar[
        (test_id, kayit["yontem"])
    ].append(kayit)


# DCG hesaplama

def dcg(puanlar):

    return sum(
        (2 ** puan - 1)
        / math.log2(sira + 2)

        for sira, puan in enumerate(puanlar)
    )


# Performans hesaplama

performans = []

test_idleri = sorted(havuz.keys())

for yontem in ["BM25", "Semantic Search"]:

    precision_listesi = []
    ndcg_listesi = []
    sure_listesi = []

    for test_id in test_idleri:

        kayitlar = sorted(
            gruplar.get((test_id, yontem), []),
            key=lambda x: x["sira"]
        )[:K]

        puanlar = [

            etiketler[
                f"{test_id}_{k['tarif_id']}"
            ]

            for k in kayitlar
        ]

        ilgili_sayisi = sum(
            p >= 1 for p in puanlar
        )

        precision = ilgili_sayisi / K

        ideal_puanlar = sorted(
            havuz[test_id].values(),
            reverse=True
        )[:K]

        ideal_dcg = dcg(ideal_puanlar)

        ndcg = (
            dcg(puanlar) / ideal_dcg
            if ideal_dcg else 0
        )

        precision_listesi.append(precision)

        ndcg_listesi.append(ndcg)

        if kayitlar:

            sure_listesi.append(
                kayitlar[0]["arama_suresi_ms"]
            )

    sonuc = {

        "yontem": yontem,

        "test_sayisi": len(test_idleri),

        "precision_at_5": statistics.mean(
            precision_listesi
        ),

        "ndcg_at_5": statistics.mean(
            ndcg_listesi
        ),

        "arama_suresi_ms": (
            statistics.mean(sure_listesi)
            if sure_listesi else None
        ),

        "sure_olculen_sorgu_sayisi": len(
            sure_listesi
        )

    }

    performans.append(sonuc)

    print("\n" + "=" * 60)

    print("Yontem:", yontem)

    print(
        "Precision@5:",
        round(sonuc["precision_at_5"], 4)
    )

    print(
        "nDCG@5:",
        round(sonuc["ndcg_at_5"], 4)
    )

    print(
        "Arama suresi:",
        round(sonuc["arama_suresi_ms"], 2)
        if sonuc["arama_suresi_ms"] is not None
        else "Olculmedi",
        "ms"
    )


# Sonuclari kaydet

with open(
    BASE / "semantic_performance_metrics.json",
    "w",
    encoding="utf-8"
) as dosya:

    json.dump(
        performans,
        dosya,
        ensure_ascii=False,
        indent=4
    )

print("\n" + "=" * 60)

print("Anlamsal arama degerlendirmesi tamamlandi.")

print(
    "Sonuclar semantic_performance_metrics.json "
    "dosyasina kaydedildi."
)