import json

from pathlib import Path

BASE = Path(__file__).resolve().parent

print("=" * 60)
print("RecipeMind AI - Top 10 Degerlendirmesi")
print("=" * 60)

# Mevcut deney kodunu oku

kod = (BASE / "evaluation.py").read_text(
    encoding="utf-8"
)

# Ilk 5 yerine ilk 10 sonucu getir

if "K = 5" not in kod:

    raise ValueError(
        "Evaluation dosyasinda K = 5 bulunamadi."
    )

kod = kod.replace(
    "K = 5",
    "K = 10",
    1
)

# Yeni sonuclari ayri dosyaya kaydet

kod = kod.replace(
    "evaluation_results.json",
    "evaluation_top10_results.json"
)

# Deneyi calistir

exec(
    compile(
        kod,
        str(BASE / "evaluation.py"),
        "exec"
    ),
    {
        "__file__": str(BASE / "evaluation.py"),
        "__name__": "__main__"
    }
)

# Sonuclari kontrol et

with open(
    BASE / "evaluation_top10_results.json",
    encoding="utf-8"
) as dosya:

    sonuclar = json.load(dosya)

print("\n" + "=" * 60)

print("Top-10 testleri tamamlandi.")

print("Toplam sonuc sayisi:", len(sonuclar))

print(
    "Sonuclar evaluation_top10_results.json "
    "dosyasina kaydedildi."
)