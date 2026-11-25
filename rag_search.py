import json
import re
import torch
import faiss
import numpy as np

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

# Veri setini yukleme
with open("data/test.jsonl", "r", encoding="utf-8") as dosya:
    tarifler = [json.loads(satir) for satir in dosya]

# Anlamsal arama modeli
arama_modeli = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2",
    local_files_only=True
)

# Kayitli vektorleri yukleme
vektorler = torch.load(
    "data/vektorler.pt",
    map_location="cpu",
    weights_only=True
).numpy().astype("float32")

faiss.normalize_L2(vektorler)

index = faiss.IndexFlatIP(vektorler.shape[1])
index.add(vektorler)

# Metin temizleme
def temizle(metin):
    return metin.replace("I", "ı").replace("İ", "i").lower()

def kelimelere_ayir(metin):
    return re.findall(r"\w+", temizle(metin))

# BM25 arama sistemi
metinler = [
    str(tarif.get("title", "")) + " " +
    str(tarif.get("ingredients", "")) + " " +
    str(tarif.get("description", ""))
    for tarif in tarifler
]

bm25 = BM25Okapi([
    kelimelere_ayir(metin) for metin in metinler
])

print("RecipeMind-AI RAG Sistemi")
print("Toplam tarif sayisi:", len(tarifler))

# Kullanici bilgileri
giris = input("Evinizdeki malzemeler: ")

malzemeler = [
    temizle(m.strip())
    for m in giris.split(",")
    if m.strip()
]

sorgu = input("Nasil bir yemek istiyorsunuz? ").strip()

if not sorgu:
    print("Lutfen yemek tercihinizi giriniz.")
    raise SystemExit

# BM25 aramasi
bm25_puanlari = bm25.get_scores(
    kelimelere_ayir(sorgu)
)

bm25_siralama = [
    i for i in np.argsort(bm25_puanlari)[::-1]
    if bm25_puanlari[i] > 0
][:100]

# FAISS aramasi
sorgu_vektoru = np.array(
    arama_modeli.encode([sorgu]),
    dtype="float32"
)

faiss.normalize_L2(sorgu_vektoru)

puanlar, indeksler = index.search(
    sorgu_vektoru, 100
)

# RRF algoritmasi
rrf_puanlari = {}

for siralama in [bm25_siralama, indeksler[0]]:
    for sira, i in enumerate(siralama, start=1):
        if i >= 0:
            rrf_puanlari[i] = (
                rrf_puanlari.get(i, 0)
                + 1 / (60 + sira)
            )

# Malzeme uyumu
sonuclar = []

for i, rrf_puani in rrf_puanlari.items():

    tarif = tarifler[i]
    gerekli = tarif.get("ingredients") or []

    mevcut = []
    eksik = []

    for g in gerekli:

        if any(
            re.search(
                r"\b" + re.escape(m) + r"\b",
                temizle(g)
            )
            for m in malzemeler
        ):
            mevcut.append(g)
        else:
            eksik.append(g)

    uyum = len(mevcut) / max(len(gerekli), 1)

    final_puan = (
        0.6 * (rrf_puani / (2 / 61))
        + 0.4 * uyum
    )

    sonuclar.append(
        (final_puan, tarif, uyum, mevcut, eksik)
    )

sonuclar.sort(key=lambda x: x[0], reverse=True)

if not sonuclar:
    print("Uygun tarif bulunamadi.")
    raise SystemExit

# En uygun tarifi secme
puan, tarif, uyum, mevcut, eksik = sonuclar[0]

print("\nONERILEN YEMEK")
print("Tarif:", tarif["title"])
print(f"Malzeme uyumu: %{uyum * 100:.1f}")
print("Mevcut malzemeler:", mevcut)
print("Eksik malzemeler:", eksik)
print("Kategori:", tarif.get("category"))
print("Tum malzemeler:", tarif.get("ingredients"))
print("Hazirlanisi:", tarif.get("instructions"))

# Uretici yapay zeka modeli
model_adi = "Qwen/Qwen2.5-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(
    model_adi,
    local_files_only=True
)

model = AutoModelForCausalLM.from_pretrained(
    model_adi,
    local_files_only=True
)

# RAG baglami
baglam = f"""
Tarif: {tarif['title']}
Kullanici tercihi: {sorgu}
Malzeme uyumu: %{uyum * 100:.1f}
Mevcut malzemeler: {mevcut}
Eksik malzemeler: {eksik}
"""

mesajlar = [
    {
        "role": "system",
        "content": "Yalnızca verilen bilgileri kullan. Yeni malzeme ekleme. Türkçe ve kısa cevap ver."
    },
    {
        "role": "user",
        "content": baglam + "\nBu tarifin neden uygun olduğunu açıkla."
    }
]

metin = tokenizer.apply_chat_template(
    mesajlar,
    tokenize=False,
    add_generation_prompt=True
)

girdiler = tokenizer(
    metin,
    return_tensors="pt"
)

with torch.inference_mode():
    cikti = model.generate(
        **girdiler,
        max_new_tokens=80,
        do_sample=False,
        repetition_penalty=1.15,
        no_repeat_ngram_size=3
    )

cevap = tokenizer.decode(
    cikti[0][girdiler["input_ids"].shape[1]:],
    skip_special_tokens=True
)

print("\nYapay zeka aciklamasi:")
print(cevap)