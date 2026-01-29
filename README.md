# 📚 Flashcards PTSI Collaboratives

## 🎯 Pourquoi ce repo ?

J'avais déjà commencé à créer des packs Anki pour mon utilisation personnelle. Je me suis dit pourquoi pas les partager à ceux qui les souhaitent et en ont besoin.

De plus, créer un repo permet à n'importe qui de participer à ce projet. **C'est une invitation !** Si vous êtes en PTSI et que vous souhaitez ajouter vos cartes/decks ou corriger des cartes pour rendre ce repo encore plus merveilleux, ne vous gênez pas !

---

## 📚 Structure du Projet

```
anki-ptsi/
├── decks/          # Fichiers CSV des flashcards (organisés par matière)
│   ├── Maths/
│   ├── SI/
│   ├── Chimie/
│   └── Anglais/
├── media/          # Images (schémas, graphiques) organisées par deck
├── output/         # Fichiers .apkg générés (ignorés par git)
├── scripts/        # Outils d'export/import/génération
└── .github/        # CI/CD pour génération automatique
```

---

## 📥 Télécharger les Decks (sans Anki installé)

Les fichiers `.apkg` sont **générés automatiquement** à chaque mise à jour du repo !

### 👉 Méthode rapide :

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
- **AnkiConnect** (addon Anki n°2055492159)
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

## 🤖 Automatisation (CI/CD)

Le workflow GitHub Actions génère automatiquement les `.apkg` :

- **Quand ?** À chaque `push` sur `main`
- **Où ?** Dans l'onglet **Actions** → **Artifacts**
- **Durée de conservation** : 30 jours

Tu peux aussi lancer manuellement le workflow depuis l'onglet Actions.

---

## 📝 Scripts Disponibles

| Script | Description |
|--------|-------------|
| `export_with_media.py` | Exporte les decks Anki → CSV + images |
| `imports_decks.py` | Importe les CSV du repo → Anki local |
| `generate_apkg.py` | Génère des `.apkg` sans Anki (utilisé par la CI) |

---

## 👥 Contribution

Toute contribution est la bienvenue ! N'hésite pas à :

- ➕ Ajouter de nouveaux decks
- ✅ Corriger des erreurs
- 📝 Améliorer la documentation
- 💡 Proposer des améliorations

Fork le projet, fais tes modifs, et ouvre une Pull Request !

---

## 🔗 Liens Utiles

- [Anki Desktop](https://apps.ankiweb.net/)
- [AnkiConnect (addon)](https://ankiweb.net/shared/info/2055492159)
- [Documentation Anki](https://docs.ankiweb.net/)

---

**Bon courage pour la PTSI ! 🚀**
