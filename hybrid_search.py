import json
import torch
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

tarifler = []

with open("data/test.jsonl", "r", encoding="utf-8") as dosya:
    for satir in dosya:
        if satir.strip():
            tarifler.append(json.loads(satir))

vektorler = torch.load("data/vektorler.pt")

print("RecipeMind-AI Hibrit Arama Sistemi")
print("Toplam tarif sayisi:", len(tarifler))

giris = input("Elinizdeki malzemeler: ")

malzemeler = [
    m.strip().lower()
    for m in giris.split(",")
    if m.strip()
]

sorgu = input("Nasil bir yemek yapmak istiyorsunuz? ")

sorgu_vektoru = model.encode(
    sorgu,
    convert_to_tensor=True
)

benzerlikler = util.cos_sim(
    sorgu_vektoru, vektorler
)[0]

sonuclar = []

for i, tarif in enumerate(tarifler):

    gerekli_malzemeler = tarif.get("ingredients") or []
    tarif_metni = " ".join(gerekli_malzemeler).lower()

    eslesen = sum(
        1 for m in malzemeler
        if m in tarif_metni
    )

    malzeme_puani = eslesen / max(len(malzemeler), 1)

    anlamsal_puan = max(0, float(benzerlikler[i]))

    hibrit_puan = (
        0.5 * malzeme_puani +
        0.5 * anlamsal_puan
    )

    eksik_malzemeler = [
        gerekli for gerekli in gerekli_malzemeler
        if not any(m in gerekli.lower() for m in malzemeler)
    ]

    sonuclar.append(
        (hibrit_puan, tarif, eksik_malzemeler)
    )

sonuclar.sort(key=lambda x: x[0], reverse=True)

print("\nHibrit arama sonuclari:")

for puan, tarif, eksikler in sonuclar[:5]:

    print("Tarif:", tarif["title"])
    print("Hibrit puan:", round(puan, 3))
    print("Kategori:", tarif.get("category"))
    print("Eksik malzemeler:", eksikler)
    print("-" * 50)