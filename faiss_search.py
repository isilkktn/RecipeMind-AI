import json
import torch
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

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

vektorler = vektorler.numpy().astype("float32")

# Vektorleri normalize etme
faiss.normalize_L2(vektorler)

# FAISS indeksini olusturma
boyut = vektorler.shape[1]

index = faiss.IndexFlatIP(boyut)

index.add(vektorler)

print("RecipeMind-AI FAISS Arama Sistemi")
print("Indekslenen tarif sayisi:", index.ntotal)

# Kullanici sorgusu
sorgu = input("Nasil bir yemek yapmak istiyorsunuz? ")

sorgu_vektoru = model.encode([sorgu])

sorgu_vektoru = np.array(
    sorgu_vektoru, dtype="float32"
)

faiss.normalize_L2(sorgu_vektoru)

# En uygun 5 tarifi bulma
puanlar, indeksler = index.search(sorgu_vektoru, 5)

print("\nFAISS arama sonuclari:")

for i, puan in zip(indeksler[0], puanlar[0]):

    tarif = tarifler[i]

    print("Tarif:", tarif["title"])
    print("Benzerlik puani:", round(float(puan), 3))
    print("Kategori:", tarif.get("category"))
    print("Malzemeler:", tarif.get("ingredients"))
    print("-" * 50)