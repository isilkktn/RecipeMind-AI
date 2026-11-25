import json
import re

def temizle(metin):
    metin = metin.replace("I", "ı").replace("İ", "i")
    return metin.lower().strip()


def malzeme_uyumu(kullanici_malzemeleri, tarif_malzemeleri):

    mevcut = []
    eksik = []

    for gerekli in tarif_malzemeleri:

        gerekli_metin = temizle(gerekli)

        if any(
            re.search(r"\b" + re.escape(m) + r"\b", gerekli_metin)
            for m in kullanici_malzemeleri
        ):
            mevcut.append(gerekli)
        else:
            eksik.append(gerekli)

    oran = len(mevcut) / max(len(tarif_malzemeleri), 1)

    return oran, mevcut, eksik


with open("data/test.jsonl", "r", encoding="utf-8") as dosya:
    tarifler = [json.loads(satir) for satir in dosya]

print("RecipeMind-AI Malzeme Uyum Sistemi")

giris = input("Evinizdeki malzemeleri giriniz: ")

malzemeler = [
    temizle(m) for m in giris.split(",")
    if m.strip()
]

sonuclar = []

for tarif in tarifler:

    oran, mevcut, eksik = malzeme_uyumu(
        malzemeler,
        tarif.get("ingredients") or []
    )

    if oran > 0:
        sonuclar.append((oran, tarif, mevcut, eksik))

sonuclar.sort(key=lambda x: x[0], reverse=True)

print("\nEn uygun yemek tarifleri:")

for oran, tarif, mevcut, eksik in sonuclar[:5]:

    print("Tarif:", tarif["title"])
    print(f"Malzeme uyumu: %{oran * 100:.1f}")
    print("Mevcut malzemeler:", mevcut)
    print("Eksik malzemeler:", eksik)
    print("-" * 50)