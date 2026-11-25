import torch
import json

from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForCausalLM


# YAPAY ZEKA MODELI

MODEL_ADI = "Qwen/Qwen2.5-1.5B-Instruct"


# MODELI BIR KEZ YUKLEME

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


# RAG ACIKLAMASI URETME

def rag_aciklama(sonuc, kullanici_tercihi):

    tarif = sonuc["tarif"]

    uyum = sonuc["uyum"]

    mevcut = sonuc["mevcut"]

    eksik = sonuc["eksik"]

    tokenizer, model = rag_modelini_yukle()

    # VERI SETINDEN GETIRILEN BAGLAM

    baglam = {
        "tarif_adi": tarif.get("title"),
        "kategori": tarif.get("category"),
        "kullanici_tercihi": kullanici_tercihi,
        "malzeme_uyumu": round(uyum * 100),
        "mevcut_malzemeler": mevcut,
        "eksik_malzemeler": eksik,
        "hazirlama_suresi": tarif.get("prep_time"),
        "tum_malzemeler": tarif.get("ingredients"),
        "hazirlanisi": tarif.get("instructions")
    }

    baglam_metni = json.dumps(
        baglam,
        ensure_ascii=False,
        indent=2
    )

    # SISTEM TALIMATLARI

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
- Eksik malzemeler varsa bunları dikkate al.
- Kullanıcıya kısa ve anlaşılır bir açıklama yap.
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

    # YAPAY ZEKA YANITI

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


# TERMINAL TESTI

if __name__ == "__main__":

    from search_engine import sistemi_yukle, tarif_ara

    print("RecipeMind AI - RAG Asistani")

    sistem = sistemi_yukle()

    malzemeler = input(
        "Evinizdeki malzemeler: "
    )

    tercih = input(
        "Nasil bir yemek istiyorsunuz? "
    )

    sonuclar = tarif_ara(

        sistem,

        malzemeler,

        tercih,

        adet=1
    )

    if sonuclar:

        sonuc = sonuclar[0]

        print(
            "\nOnerilen tarif:",
            sonuc["tarif"]["title"]
        )

        print(
            "Malzeme uyumu:",
            f"%{sonuc['uyum'] * 100:.0f}"
        )

        print(
            "\nYapay zeka aciklamasi:"
        )

        print(
            rag_aciklama(sonuc, tercih)
        )

    else:

        print("Uygun tarif bulunamadi.")