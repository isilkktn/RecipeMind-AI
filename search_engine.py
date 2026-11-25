import json
import re
import torch
import faiss
import numpy as np

from pathlib import Path
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

BASE = Path(__file__).resolve().parent


def temizle(metin):

    return str(metin).replace(
        "I", "ı"
    ).replace("İ", "i").lower().strip()


def kelimeler(metin):

    return re.findall(r"\w+", temizle(metin))


def sistemi_yukle():

    with open(
        BASE / "data/test.jsonl",
        encoding="utf-8"
    ) as dosya:

        tarifler = [
            json.loads(satir)
            for satir in dosya
            if satir.strip()
        ]

    model = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2",
        local_files_only=True
    )

    vektorler = torch.load(
        BASE / "data/vektorler.pt",
        map_location="cpu",
        weights_only=True
    ).numpy().astype("float32")

    if len(vektorler) != len(tarifler):

        raise ValueError(
            "Tarif ve vektör sayıları uyuşmuyor."
        )

    faiss.normalize_L2(vektorler)

    index = faiss.IndexFlatIP(
        vektorler.shape[1]
    )

    index.add(vektorler)

    metinler = [
        str(t.get("title", "")) + " " +
        str(t.get("ingredients", "")) + " " +
        str(t.get("description", ""))
        for t in tarifler
    ]

    bm25 = BM25Okapi([
        kelimeler(m)
        for m in metinler
    ])

    return tarifler, model, index, bm25


def malzeme_uyumu(malzemeler, gerekli):

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

    return uyum, mevcut, eksik


def tarif_ara(
    sistem,
    malzemeler,
    sorgu,
    adet=6
):

    tarifler, model, index, bm25 = sistem

    malzemeler = [
        temizle(m)
        for m in malzemeler.split(",")
        if m.strip()
    ]

    if not malzemeler or not sorgu.strip():

        return []

    bm25_puanlari = bm25.get_scores(
        kelimeler(sorgu)
    )

    bm25_siralama = [
        int(i)
        for i in np.argsort(
            bm25_puanlari
        )[::-1]
        if bm25_puanlari[i] > 0
    ][:100]

    sorgu_vektoru = np.array(
        model.encode([sorgu]),
        dtype="float32"
    )

    faiss.normalize_L2(sorgu_vektoru)

    _, indeksler = index.search(
        sorgu_vektoru, 100
    )

    rrf_puanlari = {}

    for siralama in [
        bm25_siralama,
        indeksler[0]
    ]:

        for sira, i in enumerate(
            siralama, start=1
        ):

            i = int(i)

            if i >= 0:

                rrf_puanlari[i] = (
                    rrf_puanlari.get(i, 0)
                    + 1 / (60 + sira)
                )

    sonuclar = []

    for i, rrf_puani in rrf_puanlari.items():

        tarif = tarifler[i]

        gerekli = tarif.get(
            "ingredients"
        ) or []

        uyum, mevcut, eksik = malzeme_uyumu(
            malzemeler,
            gerekli
        )

        final_puan = (
            0.6 * (rrf_puani / (2 / 61))
            + 0.4 * uyum
        )

        sonuclar.append({

            "id": i,
            "tarif": tarif,
            "puan": final_puan,
            "uyum": uyum,
            "mevcut": mevcut,
            "eksik": eksik

        })

    sonuclar.sort(
        key=lambda x: x["puan"],
        reverse=True
    )

    return sonuclar[:adet]