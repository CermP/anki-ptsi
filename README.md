# Flashcards PTSI Collaboratives

[Qu'est ce que Anki ?](https://www.ac-paris.fr/anki-l-application-pour-memoriser-et-reviser-128726) et [le site officiel](https://apps.ankiweb.net)



## Télécharger les Decks

### 👉 **[Page de téléchargement avec decks individuels](https://cermp.github.io/anki-ptsi/)**

---

## 🛠️ Installation (pour Contributeurs)

Si tu veux **contribuer** ou **modifier les decks en local** :

### Prérequis

- **Anki** (desktop) installé
- **AnkiConnect** (addon Anki n°2055492159) lien : [AnkiConnect (addon)](https://ankiweb.net/shared/info/2055492159)
- **Python 3.x** avec pip
- Un [Compte Github](https://github.com/signup)

### Étapes

```bash
# 1. Clone le repo
git clone https://github.com/CermP/anki-ptsi.git
cd anki-ptsi

# 2. Installe les dépendances Python
python3 -m pip install -r requirements.txt

# 3. Lance Anki et assure-toi qu'AnkiConnect est actif

# 4. Exporte un deck depuis Anki vers le repo
python3 scripts/export_with_media.py

# 5. Importe des decks du repo vers Anki
python3 scripts/imports_decks.py
```

---

## ➕ Comment Contribuer

### Petites corrections

1. Va dans le fichier CSV concerné (ex: `decks/Maths/suites.csv`)
2. Clique sur le crayon ✏️ pour éditer
3. Modifie les cartes
4. Commit tes changements directement sur GitHub

### Modifications plus importantes via Anki

1. Télécharge le .csv ou .apkg depuis le repo ou depuis [la page de téléchargement](https://cermp.github.io/anki-ptsi/)
2. Importe-le dans Anki avec `python3 scripts/imports_decks.py` si tu as pris le csv et que des media sont liés ou depuis anki si c'est un .apkg (le .apkg contient déjà les images)
3. Modifie les cartes dans Anki
4. Re-exporte avec `python3 scripts/export_with_media.py`
5. Commit et push les modifications

### Ajouter tes propres decks

-> Pour rendre la relecture plus simple il faut utiliser le format .csv

#### Pour cela :

1. Crée ton deck dans Anki
2. Lance `python3 scripts/export_with_media.py`
3. Le script copiera automatiquement l'image dans `media/nom_du_deck/`
4. Commit et push (le CSV + les images)

---

## Scripts Disponibles

| Script | Description |
|--------|-------------|
| `export_with_media.py` | Exporte les decks Anki → CSV + images |
| `imports_decks.py` | Importe les CSV du repo → Anki local |
| `generate_apkg.py` | Génère des `.apkg` sans Anki (effectué à chaque push) |
| `generate_index.py` | Crée la page web de téléchargement (effectué à chaque push) |

---

## Liens Utiles

- [Comment cloner le projet](https://docs.github.com/fr/repositories/creating-and-managing-repositories/cloning-a-repository)
- [🌐 Page de téléchargement](https://cermp.github.io/anki-ptsi/)
- [Anki Desktop](https://apps.ankiweb.net/)
- [AnkiConnect (addon)](https://ankiweb.net/shared/info/2055492159)
- [Documentation Anki](https://docs.ankiweb.net/)
