from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

URL = "https://lol.fandom.com/wiki/Special:RunQuery/PickBanHistory?PBH%5Bpage%5D=LCK+2024+Summer&PBH%5Btextonly%5D=Yes&_run="
HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean(champ):
    return champ.replace("\xa0", " ").strip()

def parse_row(row):
    from bs4 import Tag

    cells = row.find_all("td")
    if len(cells) < 35:
        return None

    match_info = clean(cells[0].text + " — " + cells[1].text + " vs " + cells[2].text)
    patch = clean(cells[5].text)
    winner = clean(cells[2].text)
    blue_team = clean(cells[1].text)
    red_team = clean(cells[2].text)

    blue_bans, red_bans = [], []
    blue_picks, red_picks = [], []

    for cell in cells:
        if not isinstance(cell, Tag):
            continue

        text = clean(cell.text)
        classes = cell.get("class", [])

        if "pbh-ban" in classes:
            if "pbh-blue" in classes:
                blue_bans.append(text)
            elif "pbh-red" in classes:
                red_bans.append(text)
        elif "pbh-blue" in classes:
            pick = [champ.strip() for champ in text.split(",")]
            blue_picks += pick
        elif "pbh-red" in classes:
            pick = [champ.strip() for champ in text.split(",")]
            red_picks += pick

    # Roles are always at the end: last 10 cells = 5 blue + 5 red
    blue_roles = [clean(cells[-12 + i].text) for i in range(5)]
    red_roles = [clean(cells[-7 + i].text) for i in range(5)]

    return {
        "match": match_info,
        "patch": patch,
        "winner": winner,
        "blue_team": blue_team,
        "red_team": red_team,
        "blue_bans": blue_bans,
        "red_bans": red_bans,
        "blue_picks": blue_picks,
        "red_picks": red_picks,
        "roles": {
            "blue": blue_roles,
            "red": red_roles
        }
    }

def main():
    res = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.select("table.wikitable tr")[1:]  # Skip header
    data = []

    for row in tqdm(rows):
        parsed = parse_row(row)
        if parsed:
            data.append(parsed)

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    output_file = data_dir / "lck_spring_raw.json"
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(data)} raw match entries.")

if __name__ == "__main__":
    main()