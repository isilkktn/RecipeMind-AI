
import os
import torch
import json

from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_ADI = "Qwen/Qwen2.5-1.5B-Instruct"


@lru_cache(maxsize=1)
def rag_modelini_yukle():

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ADI,
        local_files_only=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ADI,
        local_files_only=True
    )

    model.eval()

    return tokenizer, model


def bulut_aciklamasi(sonuc):

    tarif = sonuc["tarif"]
    baslik = tarif.get("title", "Bu tarif")
    uyum = round(sonuc["uyum"] * 100)
    eksik = sonuc["eksik"]

    cevap = (
        f"{baslik}, mevcut malzemelerinizle "
        f"%{uyum} uyum göstermektedir. "
    )

    if eksik:

        cevap += (
            f"Tarifi hazırlamak için {len(eksik)} "
            "eksik malzemeyi tamamlamanız gerekmektedir."
        )

    else:

        cevap += (
            "Tarifteki malzemeler isim bazında "
            "eşleşmektedir. Miktarları kontrol ediniz."
        )

    return (
        "Bulut sürümü - Kural tabanlı açıklama: "
        + cevap
    )


def rag_aciklama(sonuc, kullanici_tercihi):

    if os.environ.get("RECIPEMIND_CLOUD") == "1":

        return bulut_aciklamasi(sonuc)

    tarif = sonuc["tarif"]

    tokenizer, model = rag_modelini_yukle()

    baglam = {
        "tarif_adi": tarif.get("title"),
        "kategori": tarif.get("category"),
        "kullanici_tercihi": kullanici_tercihi,
        "malzeme_uyumu": round(sonuc["uyum"] * 100),
        "mevcut_malzemeler": sonuc["mevcut"],
        "eksik_malzemeler": sonuc["eksik"],
        "hazirlama_suresi": tarif.get("prep_time"),
        "tum_malzemeler": tarif.get("ingredients"),
        "hazirlanisi": tarif.get("instructions")
    }

    baglam_metni = json.dumps(
        baglam,
        ensure_ascii=False,
        indent=2
    )

    sistem_talimati = """
Sen RecipeMind AI isimli bir yemek tarifi asistanısın.

Görevin, verilen tarif bilgilerine dayanarak
tarifin kullanıcıya neden önerildiğini açıklamaktır.

Kurallar:
- Yalnızca verilen tarif bilgilerini kullan.
- Türkçe cevap ver.
- Yeni malzeme uydurma.
- Hazırlama süresi uydurma.
- Malzeme miktarlarının yeterli olduğunu iddia etme.
- Eksik malzemeleri dikkate al.
- En fazla üç cümle yaz.
- Verilen bağlam dışına çıkma.
"""

    mesajlar = [
        {
            "role": "system",
            "content": sistem_talimati
        },
        {
            "role": "user",
            "content": (
                "Tarif bilgileri:\n"
                + baglam_metni
                + "\n\n"
                + "Bu tarifin kullanıcıya neden "
                + "önerildiğini Türkçe açıkla."
            )
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

    girdiler = {
        anahtar: deger.to(model.device)
        for anahtar, deger in girdiler.items()
    }

    with torch.inference_mode():

        cikti = model.generate(
            **girdiler,
            max_new_tokens=160,
            do_sample=False,
            repetition_penalty=1.08,
            pad_token_id=tokenizer.eos_token_id
        )

    cevap = tokenizer.decode(
        cikti[0][girdiler["input_ids"].shape[1]:],
        skip_special_tokens=True
    )

    return cevap.strip()
