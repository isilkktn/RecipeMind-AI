import json
import torch

from pathlib import Path
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

DATA.mkdir(exist_ok=True)

DATASET_ID = "mmkocak/turkish-recipes-175K"

EMBEDDING_MODEL = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

LLM_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

print("=" * 60)
print("RecipeMind AI - Otomatik Kurulum")
print("=" * 60)

# 1. VERI SETI

veri_yolu = DATA / "test.jsonl"

if veri_yolu.exists():

    print("\n[1/4] Veri seti zaten mevcut.")

else:

    print("\n[1/4] Veri seti indiriliyor...")

    hf_hub_download(
        repo_id=DATASET_ID,
        repo_type="dataset",
        filename="test.jsonl",
        local_dir=str(DATA)
    )

with open(veri_yolu, encoding="utf-8") as dosya:

    tarifler = [
        json.loads(satir)
        for satir in dosya
        if satir.strip()
    ]

print("Toplam tarif:", len(tarifler))

# 2. EMBEDDING MODELI

print("\n[2/4] Anlamsal arama modeli hazirlaniyor...")

model = SentenceTransformer(EMBEDDING_MODEL)

print("Anlamsal arama modeli hazir.")

# 3. TARIF VEKTORLERI

vektor_yolu = DATA / "vektorler.pt"

vektorler_hazir = False

if vektor_yolu.exists():

    mevcut_vektorler = torch.load(
        vektor_yolu,
        map_location="cpu",
        weights_only=True
    )

    if mevcut_vektorler.shape == (len(tarifler), 384):

        vektorler_hazir = True

if vektorler_hazir:

    print("\n[3/4] Tarif vektorleri zaten mevcut.")

else:

    print("\n[3/4] Tarif vektorleri olusturuluyor...")

    metinler = [

        str(t.get("title", ""))
        + " "
        + str(t.get("ingredients", ""))
        + " "
        + str(t.get("description", ""))

        for t in tarifler

    ]

    vektorler = model.encode(

        metinler,

        batch_size=32,

        show_progress_bar=True,

        convert_to_tensor=True

    )

    torch.save(
        vektorler.cpu(),
        vektor_yolu
    )

    print("Tarif vektorleri kaydedildi.")

# 4. RAG DIL MODELI

print("\n[4/4] Qwen yapay zeka modeli hazirlaniyor...")

tokenizer = AutoTokenizer.from_pretrained(
    LLM_MODEL
)

llm = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL
)

print("Qwen modeli hazir.")

# KURULUM SONUCU

print("\n" + "=" * 60)

print("RECIPEMIND AI KURULUMU TAMAMLANDI")

print("=" * 60)

print("Veri seti: Hazir")
print("Anlamsal arama modeli: Hazir")
print("Tarif vektorleri: Hazir")
print("RAG dil modeli: Hazir")

print("\nUygulamayi baslatmak icin:")

print("python -m streamlit run premium_app.py")