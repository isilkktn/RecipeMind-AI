import os
import torch
import json
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

print("Yapay zeka modeli yuklendi!")

tarifler = []

with open("data/test.jsonl", "r", encoding="utf-8") as dosya:
    for satir in dosya:
        tarifler.append(json.loads(satir))

print("Toplam tarif sayisi:", len(tarifler))

metinler = []

for tarif in tarifler:
    metin = (
        str(tarif.get("title", "")) + " " +
        str(tarif.get("ingredients", "")) + " " +
        str(tarif.get("description", ""))
    )
    metinler.append(metin)

print("Tarifler analiz ediliyor...")

if os.path.exists("data/vektorler.pt"):
    vektorler = torch.load("data/vektorler.pt")
    print("Kayitli vektorler yuklendi!")
else:
    vektorler = model.encode(
        metinler,
        convert_to_tensor=True,
        show_progress_bar=True
    )

    torch.save(vektorler.cpu(), "data/vektorler.pt")
    print("Vektorler basariyla kaydedildi!")

sorgu = input("Nasil bir yemek yapmak istiyorsunuz? ")

sorgu_vektoru = model.encode(
    sorgu,
    convert_to_tensor=True
)

sonuclar = util.semantic_search(
    sorgu_vektoru,
    vektorler,
    top_k=5
)

print("\nAnlamsal arama sonuclari:")

for sonuc in sonuclar[0]:
    tarif = tarifler[sonuc["corpus_id"]]

    print("Tarif:", tarif["title"])
    print("Benzerlik puani:", round(sonuc["score"], 3))
    print("-" * 50)