import json
import math
import re
import statistics

from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent

K = 5

# ARAMA SONUCLARINI YUKLE

with open(
    BASE / "evaluation_results.json",
    encoding="utf-8"
) as dosya:

    sonuclar = json.load(dosya)


# METIN TEMIZLEME

def temizle(metin):

    return str(metin).replace(
        "I", "ı"
    ).replace("İ", "i").lower().strip()


# MALZEME UYUMU

def malzeme_uyumu(kayit):

    mevcut = [
        temizle(m)
        for m in kayit["malzemeler"].split(",")
        if m.strip()
    ]

    gerekli = kayit.get(
        "tarif_malzemeleri"
    ) or []

    eslesen = 0

    for malzeme in gerekli:

        if any(

            re.search(
                r"\b" + re.escape(m) + r"\b",
                temizle(malzeme)
            )

            for m in mevcut

        ):

            eslesen += 1

    return eslesen / max(len(gerekli), 1)


# TEKRARSIZ DEGERLENDIRME HAVUZU

havuz = {}

for kayit in sonuclar:

    anahtar = (
        kayit["test_id"],
        kayit["tarif_id"]
    )

    havuz[anahtar] = kayit


# ILGILILIK ETIKETLERI

etiket_dosyasi = BASE / "relevance_labels.json"

if etiket_dosyasi.exists():

    with open(
        etiket_dosyasi,
        encoding="utf-8"
    ) as dosya:

        etiketler = json.load(dosya)

else:

    etiketler = {}


def etiketleri_kaydet():

    with open(
        etiket_dosyasi,
        "w",
        encoding="utf-8"
    ) as dosya:

        json.dump(
            etiketler,
            dosya,
            ensure_ascii=False,
            indent=4
        )


print("=" * 60)
print("RecipeMind AI - Akademik Degerlendirme")
print("=" * 60)

print("Toplam sonuc:", len(sonuclar))

print("Tekrarsiz kayit:", len(havuz))

print("\nIlgililik puanlari:")
print("0 = Ilgisiz")
print("1 = Kismen ilgili")
print("2 = Dogrudan ilgili")


# ILGILILIK DEGERLENDIRMESI

for anahtar, kayit in sorted(havuz.items()):

    etiket_anahtari = (
        f"{anahtar[0]}_{anahtar[1]}"
    )

    if etiket_anahtari in etiketler:

        continue

    print("\n" + "-" * 60)

    print("Sorgu:", kayit["sorgu"])

    print("Tarif:", kayit["tarif_adi"])

    print("Kategori:", kayit["kategori"])

    print(
        "Tarif malzemeleri:",
        kayit["tarif_malzemeleri"]
    )

    print(
        "Hazirlama suresi:",
        kayit["hazirlama_suresi"]
    )

    while True:

        puan = input(
            "Ilgililik puani (0/1/2, cikis q): "
        ).strip().lower()

        if puan == "q":

            etiketleri_kaydet()

            print("Ilerlemeniz kaydedildi.")

            raise SystemExit

        if puan in ["0", "1", "2"]:

            etiketler[etiket_anahtari] = int(puan)

            etiketleri_kaydet()

            break

        print("Lutfen 0, 1 veya 2 giriniz.")


# SONUCLARI GRUPLANDIR

gruplar = defaultdict(list)

for kayit in sonuclar:

    anahtar = (
        kayit["test_id"],
        kayit["yontem"]
    )

    gruplar[anahtar].append(kayit)


# NDCG HESAPLAMA

def dcg(puanlar):

    return sum(

        (2 ** puan - 1) /
        math.log2(sira + 2)

        for sira, puan in enumerate(puanlar)

    )


# METRIKLER

metrikler = defaultdict(list)

for (test_id, yontem), kayitlar in gruplar.items():

    kayitlar = sorted(

        kayitlar,

        key=lambda x: x["sira"]

    )[:K]

    puanlar = [

        etiketler[
            f"{test_id}_{k['tarif_id']}"
        ]

        for k in kayitlar

    ]

    # Kismen ve dogrudan ilgili
    # sonuclar ilgili kabul edilir.

    ilgili_sayisi = sum(

        p >= 1 for p in puanlar

    )

    havuz_puanlari = [

        etiketler[f"{q}_{t}"]

        for q, t in havuz

        if q == test_id

    ]

    toplam_ilgili = sum(

        p >= 1 for p in havuz_puanlari

    )

    precision = ilgili_sayisi / K

    recall = (

        ilgili_sayisi / toplam_ilgili

        if toplam_ilgili else 0

    )

    f1 = (

        2 * precision * recall /
        (precision + recall)

        if precision + recall else 0

    )

    ideal_puanlar = sorted(

        havuz_puanlari,

        reverse=True

    )[:K]

    ideal_dcg = dcg(ideal_puanlar)

    ndcg = (

        dcg(puanlar) / ideal_dcg

        if ideal_dcg else 0

    )

    ortalama_uyum = statistics.mean(

        malzeme_uyumu(k)

        for k in kayitlar

    )

    arama_suresi = (

        kayitlar[0]["arama_suresi"] * 1000

    )

    metrikler[yontem].append({

        "test_id": test_id,

        "precision_at_5": precision,

        "recall_at_5": recall,

        "f1_at_5": f1,

        "ndcg_at_5": ndcg,

        "malzeme_uyumu": ortalama_uyum,

        "arama_suresi_ms": arama_suresi

    })


# ORTALAMA PERFORMANS

performans = []

for yontem, kayitlar in metrikler.items():

    sonuc = {

        "yontem": yontem,

        "test_sayisi": len(kayitlar)

    }

    for metrik in [

        "precision_at_5",

        "recall_at_5",

        "f1_at_5",

        "ndcg_at_5",

        "malzeme_uyumu",

        "arama_suresi_ms"

    ]:

        sonuc[metrik] = statistics.mean(

            k[metrik] for k in kayitlar

        )

    performans.append(sonuc)


# PERFORMANS SONUCLARINI KAYDET

with open(

    BASE / "performance_metrics.json",

    "w",

    encoding="utf-8"

) as dosya:

    json.dump(

        performans,

        dosya,

        ensure_ascii=False,

        indent=4

    )


# TERMINALDE SONUCLARI GOSTER

print("\n" + "=" * 60)

print("ALGORITMA PERFORMANS SONUCLARI")

print("=" * 60)

for sonuc in performans:

    print("\nYontem:", sonuc["yontem"])

    print(
        "Precision@5:",
        round(sonuc["precision_at_5"], 4)
    )

    print(
        "Recall@5 (havuz):",
        round(sonuc["recall_at_5"], 4)
    )

    print(
        "F1@5:",
        round(sonuc["f1_at_5"], 4)
    )

    print(
        "nDCG@5:",
        round(sonuc["ndcg_at_5"], 4)
    )

    print(
        "Malzeme uyumu:",
        round(sonuc["malzeme_uyumu"] * 100, 2),
        "%"
    )

    print(
        "Arama suresi:",
        round(sonuc["arama_suresi_ms"], 2),
        "ms"
    )

print("\nDegerlendirme tamamlandi.")

print(
    "Sonuclar performance_metrics.json "
    "dosyasina kaydedildi."
)