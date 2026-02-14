# Flashcards PTSI Collaboratives

[Qu'est-ce que Anki ?](https://www.ac-paris.fr/anki-l-application-pour-memoriser-et-reviser-128726) · [Site officiel](https://apps.ankiweb.net)

## Télécharger les Decks

### 👉 **[Page de téléchargement avec decks individuels](https://cermp.github.io/anki-ptsi/)**

---

## ➕ Comment Contribuer

### Prérequis

- **Anki** (desktop) installé avec **[AnkiConnect](https://ankiweb.net/shared/info/2055492159)** (add-on n°`2055492159`)
- **[AnkiCompanionApp](https://github.com/CermP/AnkiCompanionApp/releases/latest)** (macOS) — pour exporter les decks
- Un [compte GitHub](https://github.com/signup)

### Petites corrections (directement sur GitHub)

1. Va dans le fichier CSV concerné (ex: `decks/maths/suites.csv`)
2. Clique sur le crayon ✏️ pour éditer
3. Modifie les cartes, commit tes changements

### Modifier ou ajouter des decks via Anki

```bash
# 1. Clone le repo
git clone https://github.com/CermP/anki-ptsi.git
cd anki-ptsi
```

1. Crée ou modifie tes cartes dans **Anki**
2. Ouvre **[AnkiCompanionApp](https://github.com/CermP/AnkiCompanionApp/releases/latest)** → **"Export Decks & Media..."**
3. Sélectionne tes decks, choisis le dossier `anki-ptsi/` comme destination
4. Commit & push les CSV + images modifiés
5. Ouvre une **Pull Request** 🎉

> **Note macOS** : au premier lancement d'AnkiCompanionApp, faites clic droit → Ouvrir → "Ouvrir quand même"

---

## 📁 Structure du Repo

```
anki-ptsi/
├── decks/           # Fichiers CSV (versionnés avec Git)
│   ├── maths/
│   └── physique/
├── media/           # Images liées aux cartes
│   ├── suites/
│   └── mecanique/
└── scripts/         # Scripts d'automatisation
```

## Scripts Disponibles

| Script | Description |
|--------|-------------|
| `export_with_media.py` | Exporte les decks Anki → CSV + images |
| `imports_decks.py` | Importe les CSV du repo → Anki local |
| `generate_apkg.py` | Génère des `.apkg` sans Anki (effectué à chaque push) |
| `generate_index.py` | Crée la page web de téléchargement (effectué à chaque push) |

> 💡 Les scripts d'export/import sont intégrés dans **[AnkiCompanionApp](https://github.com/CermP/AnkiCompanionApp/releases/latest)**, pas besoin de les lancer manuellement.

---

## Liens Utiles

- [🌐 Page de téléchargement](https://cermp.github.io/anki-ptsi/)
- [📱 AnkiCompanionApp](https://github.com/CermP/AnkiCompanionApp/releases/latest)
- [Anki Desktop](https://apps.ankiweb.net/)
- [AnkiConnect (add-on)](https://ankiweb.net/shared/info/2055492159)
- [Comment cloner le projet](https://docs.github.com/fr/repositories/creating-and-managing-repositories/cloning-a-repository)
- [Documentation Anki](https://docs.ankiweb.net/)
