import sqlite3
import time
import requests
from fetch_log import battlelog

DB = "matches.db"

def init_db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,
        battle_time TEXT,
        mode TEXT,
        map TEXT,
        team1 TEXT,
        team2 TEXT,
        winner INTEGER
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS players (
        tag TEXT PRIMARY KEY,
        visited INTEGER DEFAULT 0
    )""")
    con.commit()
    return con

def normalize(tag):
    return "#" + tag.strip().replace("#", "").upper()

def process_match(con, m, tag):
    b = m.get("battle", {})
    if b.get("type") != "soloRanked":
        return
    teams = b.get("teams")
    if not teams or len(teams) != 2:
        return
    result = b.get("result")
    if result not in ("victory", "defeat"):
        return

    all_tags = [p["tag"] for t in teams for p in t]
    my_idx = None
    for i, t in enumerate(teams):
        if any(p["tag"] == tag for p in t):
            my_idx = i
    if my_idx is None:
        return

    winner_idx = my_idx if result == "victory" else 1 - my_idx
    match_id = m["battleTime"] + "_" + "_".join(sorted(all_tags))
    team_names = [
        ",".join(sorted(p["brawler"]["name"] for p in t)) for t in teams
    ]
    event = m.get("event", {})

    con.execute(
        "INSERT OR IGNORE INTO matches VALUES (?,?,?,?,?,?,?)",
        (match_id, m["battleTime"], event.get("mode"), event.get("map"),
         team_names[0], team_names[1], winner_idx + 1),
    )
    for t in all_tags:
        con.execute("INSERT OR IGNORE INTO players(tag) VALUES (?)", (t,))

def crawl(con, seeds, max_players):
    for s in seeds:
        con.execute("INSERT OR IGNORE INTO players(tag) VALUES (?)", (s,))
    con.commit()

    for _ in range(max_players):
        row = con.execute(
            "SELECT tag FROM players WHERE visited=0 LIMIT 1"
        ).fetchone()
        if not row:
            print("Ziyaret edilecek oyuncu kalmadı.")
            break
        tag = row[0]
        try:
            items = battlelog(tag)
        except requests.HTTPError as e:
            code = e.response.status_code
            print(tag, "-> hata", code)
            if code in (403, 429):
                print("Anahtar/IP ya da istek sınırı sorunu, durduruyorum.")
                break
            con.execute("UPDATE players SET visited=1 WHERE tag=?", (tag,))
            con.commit()
            continue

        for m in items:
            process_match(con, m, tag)
        con.execute("UPDATE players SET visited=1 WHERE tag=?", (tag,))
        con.commit()
        time.sleep(0.3)

if __name__ == "__main__":
    con = init_db()
    girdi = input("Başlangıç tag'leri (virgülle): ")
    seeds = [normalize(x) for x in girdi.split(",") if x.strip()]
    sayi = int(input("Kaç oyuncu taransın? (örn. 30): ") or 30)
    crawl(con, seeds, sayi)

    n_match = con.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    n_players = con.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    print(f"Toplam maç: {n_match} | Bilinen oyuncu: {n_players}")