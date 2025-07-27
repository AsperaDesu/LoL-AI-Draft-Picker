# 🧠 LoL AI Draft Picker

A machine learning-based draft pick assistant for **League of Legends**, trained to suggest optimal champion picks and roles based on professional play data.

---

## 🚀 Features

- 🤖 Predicts **optimal champions** and **roles** using AI
- 🏆 Trained on **historical LCK draft data**
- 🧱 Modular architecture: scraping, preprocessing, training
- 🔄 Easily extendable for new patches or metas

---

## 📦 How to Use

1. **Run** [`data_scraper.py`](https://github.com/AsperaDesu/LoL-AI-Draft-Picker/blob/main/code/data_scraper.py):
    - You may modify the `URL` variable to target a different tournament.
    ```python
    import json
    from tqdm import tqdm

    URL = "https://lol.fandom.com/wiki/Special:RunQuery/PickBanHistory?PBH%5Bpage%5D=LCK+2024+Summer&PBH%5Btextonly%5D=Yes&_run="
    HEADERS = {"User-Agent": "Mozilla/5.0"}
    ```

2. **Output**: A new `.json` file will be created in the `data/` folder. It contains scraped pick and ban data.

3. **Train the model**: Run every cell in [`training.ipynb`](https://github.com/AsperaDesu/LoL-AI-Draft-Picker/blob/main/code/training.ipynb) to start training the model.

---

## Overview
This is a project created to test my knowledge from Andrej Karpathy's NN Playlist. Noticably the implementation of Self Attention and Transformer is majorly inspired from him. 
##### Core Components & Techniques
- **Input Masking**
	Inspired from how Transformers are masked where inputs are only known until the `N`-th element.
	
- **Winner Emb**
	The usage of `winner_emb` is to encourage the model to optimize towards the winning draft and less to the losing one.
	
- **Class Emb**
	To make the model understand the composition of the team. 
	- Contains special token `START`
	
- **Position Emb**
	To distinguish first pick, last pick and anything in between
	
- **Type Emb**
	Differentiates Pick and Ban
	- Contains special token `START`

- **Score Linear Projection**
	To estimate a score to measure how "optimal" a champion is on that current patch and pass it down to a projection layer.
	
- **Team Emb**
	Blue versus Red Team's turn is different so we factor that in to the input
	- Contains special token `START`
	
- **Champ Emb**
	Every champ has different skillset, counter, and countered by.
	- Contains special token `<start>`

- **Joint Logits**
	Stores logits with the last two shape of (champ_vocab, ROLES) so the model's output contains how synergeous a champion is to all possible roles.

- **Champ and Role Loss**
	While not used/returned during forward function, it is used to help guide the model effectively.
	
- **Top K Sampling during Simulation**
	Due to concerns that the set of champions that are appropriate to pick/ban combined don't have a high enough probability to make it consistent, we only sample the 20 highest logits.

##What to be Improved
- [ ] Add full flex-pick role probability modeling
- [ ] Model can reevaluate roles after a flex pick
- [ ] Deploy as a public web app or Discord bot
- [ ] Closer attention to Trio ([Top, Mid, Jungle], [Bot, Support, Jungle]) and Duo (Bot and Support) synergies

---
## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Made by [@AsperaDesu](https://github.com/AsperaDesu) — the mind behind the project
