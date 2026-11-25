import json

print("RecipeMind-AI sistemine hoş geldiniz!")

with open("data/test.jsonl", "r", encoding="utf-8") as dosya:
    tarifler = [json.loads(satir) for satir in dosya]

print("Toplam tarif sayısı:", len(tarifler))

giris = input("Malzemelerinizi virgülle ayırarak giriniz: ")

malzemeler = list(set(
    m.strip().lower() for m in giris.split(",") if m.strip()
))

sonuclar = []

for tarif in tarifler:
    tarif_malzemeleri = str(tarif.get("ingredients", "")).lower()

    puan = 0

    for malzeme in malzemeler:
        if malzeme in tarif_malzemeleri:
            puan += 1

    if puan > 0:
        sonuclar.append((puan, tarif))

sonuclar.sort(key=lambda x: x[0], reverse=True)

print("\nÖnerilen yemek tarifleri:")

for puan, tarif in sonuclar[:10]:
    oran = (puan / len(malzemeler)) * 100

    print(f"{tarif['title']} - Eşleşme: %{oran:.0f}")
    print("Malzemeler:", tarif.get("ingredients"))
    print("Kategori:", tarif.get("category"))
    print("Hazırlama süresi:", tarif.get("prep_time"))
    eksik_malzemeler = []

    for gerekli in tarif.get("ingredients", []) or []:
        if not any(m in gerekli.lower() for m in malzemeler):
            eksik_malzemeler.append(gerekli)

    print("Eksik malzemeler:", eksik_malzemeler)
    print("-" * 50)