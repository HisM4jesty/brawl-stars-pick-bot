import json
from fetch_log import battlelog

tag = input("Oyuncu tag'i: ")
for m in battlelog(tag):
    if m.get("battle", {}).get("type") == "soloRanked":
        print(json.dumps(m, indent=2, ensure_ascii=False))
        break
    