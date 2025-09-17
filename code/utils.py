import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import os
import tempfile

default_patch = '14.8.1'
def get_champion_classes(patch=default_patch):
    url = f"https://ddragon.leagueoflegends.com/cdn/{patch}/data/en_US/champion.json"
    
    resp = requests.get(url)
    data = resp.json()["data"]
    
    classes = {}
    for champ, info in data.items():
        classes[info["name"]] = info["tags"]
    
    return classes

def get_champion_scores(patch=default_patch):
    url = f'https://www.metasrc.com/lol/{patch}/stats?ranks=grandmaster,challenger'

    temp_profile = tempfile.mkdtemp()
    options = Options()
    options.add_argument("--headless")
    options.add_argument(f"--user-data-dir={temp_profile}")  # Prevent profile collision
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    print(f"Opening MetaSRC patch {patch}...")
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    table = soup.find('table')
    if not table:
        raise Exception("Stats table not found.")

    data = []
    rows = table.find_all('tr')[1:]  # Skip header

    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            continue

        champ = cols[0].find("span").text.strip()
        role = cols[1].get_text(strip=True).lower()
        score = cols[3].get_text(strip=True)
        role = role if role != 'adc' else 'bot'
        data.append({
            "champion": champ,
            "role": role,
            "score": score
        })

    return pd.DataFrame(data)

def load_or_fetch_scores(patch=default_patch):
    file_path = f"champion_scores_{patch}.csv"
    if os.path.exists(file_path):
        print(f"Loading cached scores for patch {patch}")
        df = pd.read_csv(file_path)
        print("-Loading completed")
        return df
    else:
        print(f"Fetching scores for patch {patch} from MetaSRC")
        df = get_champion_scores(patch)
        df.to_csv(file_path, index=False)
        print("-Fetching completed")
        return df

def tokenize_draft(match, tokenizer):
    match["blue_picks"] = tokenizer.encode(match["blue_picks"])
    match["red_picks"] = tokenizer.encode(match["red_picks"])
    match["blue_bans"] = tokenizer.encode(match["blue_bans"])
    match["red_bans"] = tokenizer.encode(match["red_bans"])
    return match

def tokenize_roles(match, tokenizer):
    match["blue_roles"] = tokenizer.encodeRole(match['roles']['blue'])
    match["red_roles"] = tokenizer.encodeRole(match['roles']['red'])
    return match

def drop_raw_picks_bans(match):
    for key in ["match", "blue_team", "red_team", "winner", "roles"]:
        match.pop(key, None)
    return match
