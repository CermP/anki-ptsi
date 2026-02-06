import json
import urllib.request
import os
import csv
import html
import re

# --- CONFIGURATION AUTOMATIQUE DES CHEMINS ---
# On trouve le chemin du script actuel (scripts/imports_decks.py)
SCRIPT_PATH = os.path.abspath(__file__)
# On récupère le dossier du script (scripts/)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
# On remonte d'un cran pour avoir la racine du projet (Anki-PTSI/)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

# On définit les dossiers par rapport à cette racine
DECKS_DIR = os.path.join(BASE_DIR, "decks")
MEDIA_DIR = os.path.join(BASE_DIR, "media")

ANKI_URL = "http://localhost:8765"

# --- FONCTIONS ---

def request(action, **params):
    """Communique avec Anki via AnkiConnect."""
    try:
        response = json.load(urllib.request.urlopen(urllib.request.Request(ANKI_URL, json.dumps({
            "action": action,
            "params": params,
            "version": 6
        }).encode("utf-8"))))
        if response.get("error") is not None:
            raise Exception(response["error"])
        return response
    except Exception as e:
        print(f"\n[ERREUR] Impossible de connecter à Anki : {e}")
        print("Vérifiez qu'Anki est ouvert et que l'addon AnkiConnect est installé.")
        return None

def get_model_name():
    """Récupère le premier modèle disponible dans Anki."""
    response = request("modelNames")
    if response and response.get("result"):
        models = response.get("result", [])
        if models:
            # On prend le 2ème modèle s'il existe (souvent "Basic"), sinon le 1er
            chosen = models[1] if len(models) > 1 else models[0]
            print(f"  📋 Utilisation du modèle : {chosen}")
            return chosen
    print("  ❌ Aucun modèle trouvé dans Anki")
    return None

def get_model_field_names(model_name):
    """Récupère les noms des champs d'un modèle Anki."""
    response = request("modelFieldNames", modelName=model_name)
    if response and response.get("result"):
        field_names = response.get("result", [])
        if field_names:
            print(f"  📝 Champs du modèle : {', '.join(field_names)}")
            return field_names
    print(f"  ❌ Impossible de récupérer les champs du modèle {model_name}")
    return None

def add_media_to_anki(filename, target_dir):
    """Ajoute un fichier média à Anki via AnkiConnect."""
    # On cherche dans le sous-dossier spécifique (ex: media/maths/)
    filepath = os.path.join(MEDIA_DIR, target_dir, filename)
    
    if not os.path.exists(filepath):
        # Si pas trouvé, on cherche aussi à la racine de media/ au cas où
        filepath_root = os.path.join(MEDIA_DIR, filename)
        if os.path.exists(filepath_root):
            filepath = filepath_root
        else:
            return None
    
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        import base64
        encoded = base64.b64encode(data).decode('utf-8')
        response = request("storeMediaFile", filename=filename, data=encoded)
        if response and response.get("result"):
            return filename
        return None
    except Exception:
        return None

def process_media_paths(text, target_dir):
    """Transforme les chemins relatifs en chemins Anki (<img src="image.jpg">)."""
    text = text.replace('""', '"')
    # Regex pour trouver src="../media/..." et garder juste le nom du fichier
    pattern = r'<img[^>]+src="(?:\.\./)*media\/[^/]+\/([^"]+)"([^>]*)>'
    replacement = r'<img src="\1"\2>'
    processed = re.sub(pattern, replacement, text)
    return processed

def add_images_from_text(text, target_dir):
    """Cherche toutes les images dans le texte et les ajoute à Anki."""
    pattern = r'src="([^"]+)"'
    matches = re.findall(pattern, text)
    for filename in matches:
        if filename.startswith('http') or filename.startswith('..'):
            continue
        add_media_to_anki(filename, target_dir)

def process_csv_for_anki(csv_path, deck_name, target_dir, model_name, field_names):
    cards = []
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            for row_idx, row in enumerate(reader, 1):
                if not row or all(cell.strip() == '' for cell in row) or len(row) < 2:
                    continue
                
                front = row[0].strip()
                back = row[1].strip()
                tags = row[2].strip() if len(row) > 2 else ""

                if front.startswith('"') and front.endswith('"'): front = front[1:-1]
                if back.startswith('"') and back.endswith('"'): back = back[1:-1]
                front = front.replace('""', '"')
                back = back.replace('""', '"')

                front = process_media_paths(front, target_dir)
                back = process_media_paths(back, target_dir)

                add_images_from_text(back, target_dir)
                add_images_from_text(front, target_dir)

                if not front.strip() and not back.strip():
                    continue

                cards.append({
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": {
                        field_names[0]: front,
                        field_names[1]: back
                    },
                    "tags": tags.split() if tags else [],
                    "options": {"allowDuplicate": False, "duplicateScope": "deck"}
                })
    except Exception as e:
        print(f"    ❌ Erreur CSV : {e}")
        return []
    return cards

def create_deck_if_needed(deck_name):
    response = request("deckNames")
    if not response: return False
    if deck_name not in response.get("result", []):
        request("createDeck", deck=deck_name)
        print(f"  ✨ Créé le deck : {deck_name}")
    return True

def add_notes_to_anki(cards):
    if not cards: return 0
    response = request("addNotes", notes=cards)
    if response:
        results = response.get("result", [])
        successful = len([r for r in results if r is not None])
        return successful
    return 0

def find_all_csvs(root_dir):
    """Trouve récursivement tous les fichiers CSV."""
    csv_files = []
    if not os.path.exists(root_dir):
        return []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                # On garde le chemin relatif par rapport à DECKS_DIR
                rel_path = os.path.relpath(os.path.join(dirpath, filename), root_dir)
                csv_files.append(rel_path)
    return sorted(csv_files)

def get_media_folder_for_csv(csv_filename):
    # On nettoie le nom pour deviner le dossier média
    clean_name = os.path.basename(csv_filename).replace('.csv', '')
    # Logique simple : essayer de trouver un dossier qui correspond
    parts = clean_name.replace('-', ' ').replace('_', ' ').split()
    # On retourne le dossier complet relatif si besoin, ou juste un nom slugifié
    # Pour l'instant on garde une logique simple basée sur le nom
    return clean_name.lower().replace(" ", "_")

def main():
    test = request("deckNames")
    if not test:
        print("\n❌ AnkiConnect n'est pas accessible. Assurez-vous qu'Anki est ouvert.")
        return

    model_name = get_model_name()
    if not model_name: return
    
    field_names = get_model_field_names(model_name)
    if not field_names or len(field_names) < 2: 
        print("❌ Le modèle doit avoir au moins 2 champs (ex: Recto, Verso)")
        return

    # Utilisation de find_all_csvs pour chercher dans les sous-dossiers
    csv_files = find_all_csvs(DECKS_DIR)
    
    if not csv_files:
        print(f"\n❌ Aucun fichier CSV trouvé dans {DECKS_DIR}")
        return

    print("\n--- FICHIERS CSV DISPONIBLES ---")
    for index, filename in enumerate(csv_files):
        print(f"[{index}] {filename}")

    user_input = input("\nEntrez les numéros à importer (séparés par une virgule, ou 'all') : ")

    target_files = []
    if user_input.lower().strip() == 'all' or user_input.strip() == '':
        target_files = csv_files
    else:
        try:
            indices = [int(x.strip()) for x in user_input.split(",")]
            for i in indices:
                if 0 <= i < len(csv_files):
                    target_files.append(csv_files[i])
        except ValueError:
            print("[ERREUR] Saisie invalide.")
            return

    print(f"\nDébut de l'import pour {len(target_files)} fichier(s)...\n")
    total_added = 0

    for csv_rel_path in target_files:
        csv_path = os.path.join(DECKS_DIR, csv_rel_path)
        csv_filename = os.path.basename(csv_rel_path)
        
        # Reconstruction du nom du deck
        deck_name = csv_filename.replace('.csv', '').replace('-', '::').replace('_', ' ')
        target_dir = get_media_folder_for_csv(csv_filename)

        print(f"📥 Import de '{csv_filename}'...")
        if not create_deck_if_needed(deck_name): continue

        cards = process_csv_for_anki(csv_path, deck_name, target_dir, model_name, field_names)
        if cards:
            total_added += add_notes_to_anki(cards)
            print()
        else:
            print(f"   ⚠️  Aucune carte trouvée\n")

    print(f"--- Terminé ! {total_added} cartes importées au total ---")

if __name__ == "__main__":
    main()
10