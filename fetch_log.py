import os
import sys
import requests

TOKEN = os.environ.get("BS_TOKEN")
BASE = "https://api.brawlstars.com/v1"

def battlelog(tag):
    tag = tag.replace("#", "").upper()
    r = requests.get(
        f"{BASE}/players/%23{tag}/battlelog",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["items"]

if __name__ == "__main__":
    if not TOKEN:
        sys.exit("BS_TOKEN ortam değişkeni ayarlı değil.")
    tag = input("Oyuncu tag'i (örn. #ABC123): ")
    for m in battlelog(tag):
        event = m.get("event", {})
        b = m.get("battle", {})
        print("-" * 40)
        print("Zaman :", m.get("battleTime"))
        print("Mod   :", event.get("mode"), "| Map:", event.get("map"))
        print("Tür   :", b.get("type"), "| Sonuç:", b.get("result"))
        for i, takim in enumerate(b.get("teams", [])):
            adlar = [p["brawler"]["name"] for p in takim]
            print(f"Takım {i + 1}:", ", ".join(adlar))