import sqlite3
from build_data import istatistik_hesapla, DB

def takim_puani(data, harita, takim, rakip, counter_kullan):
    toplam = 0
    for b in takim:
        toplam += data["map_score"].get(harita, {}).get(b, [0, 0])[0]
        if counter_kullan:
            for r in rakip:
                toplam += data["counter"].get(b, {}).get(r, [0, 0])[0]
    return toplam

def olc(data, test, counter_kullan):
    dogru = toplam = 0
    for harita, t1, t2, winner in test:
        a, b = t1.split(","), t2.split(",")
        p1 = takim_puani(data, harita, a, b, counter_kullan)
        p2 = takim_puani(data, harita, b, a, counter_kullan)
        if p1 == p2:
            continue  # berabere, tahmin yok
        tahmin = 1 if p1 > p2 else 2
        toplam += 1
        dogru += (tahmin == winner)
    return dogru, toplam

def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT map, team1, team2, winner FROM matches ORDER BY battle_time"
    ).fetchall()
    kesim = int(len(rows) * 0.8)
    egitim, test = rows[:kesim], rows[kesim:]
    data = istatistik_hesapla(egitim)
    print(f"Eğitim: {len(egitim)} maç | Test: {len(test)} maç")

    for ad, c in [("Sadece map puanı", False), ("Map + counter", True)]:
        d, t = olc(data, test, c)
        if t:
            print(f"{ad}: {d}/{t} doğru (%{100 * d / t:.1f})")
        else:
            print(f"{ad}: tahmin yapılamadı (veri çok az)")

if __name__ == "__main__":
    main()