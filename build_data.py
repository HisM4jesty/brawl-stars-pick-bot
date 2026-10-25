import json
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta, timezone

DB = "matches.db"
K = 10          # yumuşatma: az maçlı sonuçlar 0'a doğru çekilir
MIN_GAMES = 3   # bundan az maçı olan kayıtlar atılır
DAYS = None     # örn. 28 yazarsan sadece son 28 günün maçları kullanılır

def skor(wins, games):
    wr = (wins + K * 0.5) / (games + K)
    return round((wr - 0.5) * 100, 2)

def istatistik_hesapla(rows):
    map_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    counter_stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))

    for harita, t1, t2, winner in rows:
        takimlar = [t1.split(","), t2.split(",")]
        for i, takim in enumerate(takimlar):
            kazandi = 1 if winner == i + 1 else 0
            rakip = takimlar[1 - i]
            for b in takim:
                s = map_stats[harita][b]
                s[0] += kazandi
                s[1] += 1
                for r in rakip:
                    if r == b:
                        continue
                    c = counter_stats[b][r]
                    c[0] += kazandi
                    c[1] += 1

    data = {"map_score": {}, "counter": {}}
    for harita, bs in map_stats.items():
        d = {b: [skor(w, g), g] for b, (w, g) in bs.items() if g >= MIN_GAMES}
        if d:
            data["map_score"][harita] = d
    for a, rs in counter_stats.items():
        d = {r: [skor(w, g), g] for r, (w, g) in rs.items() if g >= MIN_GAMES}
        if d:
            data["counter"][a] = d
    return data

def maclari_yukle(con, gun=DAYS):
    sorgu = "SELECT map, team1, team2, winner FROM matches"
    if gun:
        sinir = (datetime.now(timezone.utc) - timedelta(days=gun)).strftime("%Y%m%dT%H%M%S")
        return con.execute(sorgu + " WHERE battle_time >= ?", (sinir,)).fetchall()
    return con.execute(sorgu).fetchall()

def main():
    con = sqlite3.connect(DB)
    rows = maclari_yukle(con)
    data = istatistik_hesapla(rows)
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    n_counter = sum(len(v) for v in data["counter"].values())
    print(f"{len(rows)} maç işlendi.")
    print(f"Map sayısı: {len(data['map_score'])} | Counter çifti: {n_counter}")

if __name__ == "__main__":
    main()