import os
import json
import runpy
import torch
import streamlit as st

from pathlib import Path
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

DATA.mkdir(exist_ok=True)

os.chdir(BASE)
os.environ["RECIPEMIND_CLOUD"] = "1"

DATASET_ID = "mmkocak/turkish-recipes-175K"

MODEL_ID = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


@st.cache_resource(show_spinner=False)
def bulut_kurulumu():

    veri_yolu = DATA / "test.jsonl"
    vektor_yolu = DATA / "vektorler.pt"

    if not veri_yolu.exists():

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

    model = SentenceTransformer(
        MODEL_ID,
        device="cpu"
    )

    if not vektor_yolu.exists():

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
            batch_size=16,
            show_progress_bar=True,
            convert_to_tensor=True
        )

        torch.save(
            vektorler.cpu(),
            vektor_yolu
        )

    return True


with st.spinner("RecipeMind AI hazırlanıyor..."):

    bulut_kurulumu()


runpy.run_path(
    str(BASE / "premium_app.py"),
    run_name="__main__"
)