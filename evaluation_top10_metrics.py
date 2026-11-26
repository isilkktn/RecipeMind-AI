import json
import math
import statistics

from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent

# Arama sonuclarini yukle

with open(
    BASE / "evaluation_top10_results.json",
    encoding="utf-8"
) as dosya:

    sonuclar = json.load(dosya)

# Ilgililik etiketlerini yukle

with open(
    BASE / "relevance_top10_labels.json",
    encoding="utf-8"
) as dosya:

    etiketler = json.load(dosya)

# Degerlendirme havuzu

havuz = defaultdict(dict)

gruplar = defaultdict(list)

for kayit in sonuclar:

    test_id = kayit["test_id"]

    tarif_id = kayit["tarif_id"]

    anahtar = f"{test_id}_{tarif_id}"

    if anahtar not in etiketler:

        raise ValueError(
            f"Eksik ilgililik etiketi: {anahtar}"
        )

    puan = etiketler[anahtar]

    if puan not in [0, 1, 2]:

        raise ValueError(
            f"Gecersiz ilgililik puani: {anahtar}"
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


# nDCG@10 hesaplama

metrikler = defaultdict(list)

for (test_id, yontem), kayitlar in gruplar.items():

    kayitlar = sorted(

        kayitlar,

        key=lambda x: x["sira"]

    )[:10]

    puanlar = [

        etiketler[
            f"{test_id}_{k['tarif_id']}"
        ]

        for k in kayitlar

    ]

    ideal_puanlar = sorted(

        havuz[test_id].values(),

        reverse=True

    )[:10]

    ideal_dcg = dcg(ideal_puanlar)

    ndcg = (

        dcg(puanlar) / ideal_dcg

        if ideal_dcg else 0

    )

    metrikler[yontem].append(ndcg)


# Ortalama sonuclar

performans = []

print("=" * 60)

print("RECIPEMIND AI - NDCG@10 SONUCLARI")

print("=" * 60)

for yontem, puanlar in metrikler.items():

    ortalama = statistics.mean(puanlar)

    performans.append({

        "yontem": yontem,

        "test_sayisi": len(puanlar),

        "ndcg_at_10": ortalama

    })

    print(
        yontem,
        ":",
        round(ortalama, 4)
    )


# Sonuclari kaydet

with open(

    BASE / "performance_top10_metrics.json",

    "w",

    encoding="utf-8"

) as dosya:

    json.dump(

        performans,

        dosya,

        ensure_ascii=False,

        indent=4

    )

print("\nDegerlendirme tamamlandi.")

print(
    "Sonuclar performance_top10_metrics.json "
    "dosyasina kaydedildi."
)