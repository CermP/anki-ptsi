# 📚 Flashcards PTSI Collaboratives

## 🌐 Télécharger les Decks (Recommandé)

### 👉 **[Page de téléchargement avec decks individuels](https://cermp.github.io/anki-ptsi/)**

Tous les decks sont disponibles **individuellement** sur notre site web !
- ✅ Téléchargement direct de chaque deck `.apkg`
- ✅ Organisés par matière (Maths, SI, Physique, Chimie, Anglais)
- ✅ Mis à jour automatiquement à chaque push
- ✅ Aucune installation requise

---

## 📦 Méthode Alternative (tous les decks en un seul zip)

### 👉 Lien de téléchargement direct (Dernière version)
[**📥 Télécharger tous les decks (.zip)**](https://nightly.link/CermP/anki-ptsi/workflows/build_decks.yml/main/anki-decks.zip)
_(Ce lien pointe toujours vers la version la plus récente générée par GitHub Actions)_

### 👉 Méthode manuelle (si le lien ne fonctionne pas) :

1. Va dans l'onglet **[Actions](https://github.com/CermP/anki-ptsi/actions)** du repo
2. Clique sur le dernier workflow réussi (✅ vert)
3. Descends jusqu'à la section **Artifacts**
4. Télécharge **anki-decks.zip**
5. Décompresse et importe les `.apkg` dans Anki (mobile ou desktop)

---

## 🛠️ Installation (pour Contributeurs)

Si tu veux **contribuer** ou **modifier les decks en local** :

### Prérequis

- **Anki** (desktop) installé
- **AnkiConnect** (addon Anki n°2055492159) lien : [AnkiConnect (addon)](https://ankiweb.net/shared/info/2055492159)
- **Python 3.x** avec pip

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

### Méthode 1 : Édition Directe (petites corrections)

1. Va dans le fichier CSV concerné (ex: `decks/Maths/suites.csv`)
2. Clique sur le crayon ✏️ pour éditer
3. Modifie les cartes
4. Commit tes changements directement sur GitHub

### Méthode 2 : Via Anki (gros changements)

1. Télécharge le CSV depuis le repo
2. Importe-le dans Anki avec `python3 scripts/imports_decks.py`
3. Modifie les cartes dans Anki
4. Re-exporte avec `python3 scripts/export_with_media.py`
5. Commit et push les modifications

### Ajouter des Images

1. Crée ou modifie une carte avec l'image dans Anki
2. Lance `python3 scripts/export_with_media.py`
3. Le script copiera automatiquement l'image dans `media/nom_du_deck/`
4. Commit et push (le CSV + les images)

---

## 📝 Scripts Disponibles

| Script | Description |
|--------|-------------|
| `export_with_media.py` | Exporte les decks Anki → CSV + images |
| `imports_decks.py` | Importe les CSV du repo → Anki local |
| `generate_apkg.py` | Génère des `.apkg` sans Anki (utilisé par la CI) |
| `generate_index.py` | Crée la page web de téléchargement (utilisé par la CI) |

---

## 🔗 Liens Utiles

- [🌐 Page de téléchargement](https://cermp.github.io/anki-ptsi/)
- [Anki Desktop](https://apps.ankiweb.net/)
- [AnkiConnect (addon)](https://ankiweb.net/shared/info/2055492159)
- [Documentation Anki](https://docs.ankiweb.net/)

---

## 🚀 Comment ça marche ?

1. **Tu modifies un CSV** ou tu exportes un deck depuis Anki
2. **Tu push sur GitHub**
3. **GitHub Actions** lance automatiquement :
   - Génération des fichiers `.apkg` individuels
   - Création de la page web avec les liens de téléchargement
   - Déploiement sur GitHub Pages
4. **C'est en ligne** à [cermp.github.io/anki-ptsi](https://cermp.github.io/anki-ptsi/) !
