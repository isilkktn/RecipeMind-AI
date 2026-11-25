import json
import re
import torch
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util

# Yapay zeka modelini yukleme
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# Veri setini okuma
with open("data/test.jsonl", "r", encoding="utf-8") as dosya:
    tarifler = [json.loads(satir) for satir in dosya]

# Kayitli vektorleri yukleme
vektorler = torch.load(
    "data/vektorler.pt",
    map_location="cpu",
    weights_only=True
)

# Tarif metinlerini hazirlama
metinler = []

for tarif in tarifler:
    metin = (
        str(tarif.get("title", "")) + " " +
        str(tarif.get("ingredients", "")) + " " +
        str(tarif.get("description", ""))
    )
    metinler.append(metin)

def kelimelere_ayir(metin):
    metin = metin.replace("I", "ı").replace("İ", "i")
    return re.findall(r"\w+", metin.lower())

# BM25 modelini olusturma
tokenler = [kelimelere_ayir(metin) for metin in metinler]

bm25 = BM25Okapi(tokenler)

print("RecipeMind-AI Gelismis Hibrit Arama")
print("Toplam tarif sayisi:", len(tarifler))

sorgu = input("Nasil bir yemek yapmak istiyorsunuz? ").strip()

if not sorgu:
    print("Lutfen bir arama sorgusu giriniz.")
    raise SystemExit

# BM25 aramasi
bm25_puanlari = bm25.get_scores(
    kelimelere_ayir(sorgu)
)

bm25_siralama = [
    i for i in np.argsort(bm25_puanlari)[::-1]
    if bm25_puanlari[i] > 0
][:100]

# Anlamsal arama
sorgu_vektoru = model.encode(
    sorgu,
    convert_to_tensor=True
).cpu()

anlamsal_puanlar = util.cos_sim(
    sorgu_vektoru,
    vektorler
)[0]

anlamsal_siralama = torch.argsort(
    anlamsal_puanlar,
    descending=True
).tolist()[:100]

# RRF algoritmasi
rrf_puanlari = {}
k = 60

for siralama in [bm25_siralama, anlamsal_siralama]:
    for sira, indeks in enumerate(siralama, start=1):
        rrf_puanlari[indeks] = (
            rrf_puanlari.get(indeks, 0)
            + 1 / (k + sira)
        )

sonuclar = sorted(
    rrf_puanlari.items(),
    key=lambda x: x[1],
    reverse=True
)

# Sonuclari gosterme
print("\nRRF Hibrit Arama Sonuclari:")

for indeks, puan in sonuclar[:5]:

    tarif = tarifler[indeks]

    print("Tarif:", tarif["title"])
    print("RRF puani:", round(puan, 5))
    print("Kategori:", tarif.get("category"))
    print("Malzemeler:", tarif.get("ingredients"))
    print("-" * 50)