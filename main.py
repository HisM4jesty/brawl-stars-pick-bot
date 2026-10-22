import json

with open("data.json", encoding="utf-8") as f:
    data = json.load(f)

def oner(harita, rakipler, banlar, sayi=5):
    skorlar = {}
    for brawler, puan in data["map_score"][harita].items():
        if brawler in banlar or brawler in rakipler:
            continue
        toplam = puan
        for r in rakipler:
            toplam += data["counter"].get(brawler, {}).get(r, 0)
        skorlar[brawler] = toplam
    return sorted(skorlar.items(), key=lambda x: -x[1])[:sayi]

def liste_al(mesaj):
    girdi = input(mesaj).strip()
    if not girdi:
        return []
    return [x.strip() for x in girdi.split(",")]

if __name__ == "__main__":
    print("Haritalar:", ", ".join(data["map_score"].keys()))
    harita_girdi = input("Harita: ").strip().lower()
    harita = next((h for h in data["map_score"] if h.lower() == harita_girdi), None)
    if harita is None:
        print("Bu harita data.json içinde yok.")
    else:
        rakipler = liste_al("Rakip brawler'lar (virgülle): ")
        banlar = liste_al("Banlar (virgülle): ")
        for i, (brawler, skor) in enumerate(oner(harita, rakipler, banlar), 1):
            print(f"{i}. {brawler}  (skor: {skor})")