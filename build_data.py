import json
import sqlite3
from collections import defaultdict

DB = "matches.db"
K = 10          # yumuşatma: az maçlı sonuçlar 0'a doğru çekilir
MIN_GAMES = 2   # bundan az maçı olan kayıtlar atılır

def skor(wins, games):
    wr = (wins + K * 0.5) / (games + K)
    return round((wr - 0.5) * 100, 2)

def main():
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT map, team1, team2, winner FROM matches").fetchall()

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
        d = {b: skor(w, g) for b, (w, g) in bs.items() if g >= MIN_GAMES}
        if d:
            data["map_score"][harita] = d
    for a, rs in counter_stats.items():
        d = {r: skor(w, g) for r, (w, g) in rs.items() if g >= MIN_GAMES}
        if d:
            data["counter"][a] = d

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    n_counter = sum(len(v) for v in data["counter"].values())
    print(f"{len(rows)} maç işlendi.")
    print(f"Map sayısı: {len(data['map_score'])} | Counter çifti: {n_counter}")

if __name__ == "__main__":
    main()