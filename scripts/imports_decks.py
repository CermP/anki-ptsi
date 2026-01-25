import json
import urllib.request
import os
import csv
import html
import re

# --- CONFIGURATION ---
DECKS_DIR = "../decks"
MEDIA_DIR = "../media"
ANKI_URL = "http://localhost:8765"

def request(action, **params):
    """
    Communique avec Anki via AnkiConnect.
    """
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
    """
    Récupère le premier modèle disponible dans Anki.
    """
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
    """
    Récupère les noms des champs d'un modèle Anki.
    """
    response = request("modelFieldNames", modelName=model_name)
    if response and response.get("result"):
        field_names = response.get("result", [])
        if field_names:
            print(f"  📝 Champs du modèle : {', '.join(field_names)}")
            return field_names
    print(f"  ❌ Impossible de récupérer les champs du modèle {model_name}")
    return None

def add_media_to_anki(filename, target_dir):
    """
    Ajoute un fichier média à Anki via AnkiConnect.
    """
    filepath = os.path.join(MEDIA_DIR, target_dir, filename)
    
    if not os.path.exists(filepath):
        # On ne spamme pas l'erreur si le fichier n'existe pas, c'est peut-être une image web
        return None
    
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        import base64
        encoded = base64.b64encode(data).decode('utf-8')
        
        response = request("storeMediaFile", 
                          filename=filename,
                          data=encoded)
        
        if response and response.get("result"):
            return filename
        else:
            return None
    except Exception as e:
        return None

def process_media_paths(text, target_dir):
    """
    Transforme les chemins relatifs en chemins Anki.
    ../media/dossier_media/image.jpg  →  <img src='image.jpg'>
    """
    # D'abord, dé-échapper les guillemets doublés du CSV (ex: src=""..."" -> src="...")
    text = text.replace('""', '"')
    
    # Regex pour trouver les chemins d'images relatifs
    # On cherche : src="../media/nom_dossier/nom_fichier.ext"
    pattern = r'<img[^>]+src="\.\.\/media\/[^/]+\/([^"]+)"([^>]*)>'
    replacement = r'<img src="\1"\2>'
    
    processed = re.sub(pattern, replacement, text)
    return processed

def add_images_from_text(text, target_dir):
    """
    Cherche toutes les images dans le texte et les ajoute à Anki.
    """
    # Regex simple pour trouver tous les src="..."
    pattern = r'src="([^"]+)"'
    matches = re.findall(pattern, text)
    
    for filename in matches:
        if filename.startswith('http') or filename.startswith('..'):
            continue
        add_media_to_anki(filename, target_dir)

def process_csv_for_anki(csv_path, deck_name, target_dir, model_name, field_names):
    """
    Lit un fichier CSV et prépare les cartes pour l'import.
    Traite les chemins d'images pour qu'Anki les comprenne.
    """
    cards = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            # IMPORTANT : csv.QUOTE_MINIMAL permet de gérer les guillemets autour des champs
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            
            for row_idx, row in enumerate(reader, 1):
                # Ignorer les lignes vides ou incomplètes
                if not row or all(cell.strip() == '' for cell in row) or len(row) < 2:
                    continue
                
                front = row[0].strip()
                back = row[1].strip()
                tags = row[2].strip() if len(row) > 2 else ""
                
                # Nettoyage manuel des guillemets si le CSV Reader a échoué (sécurité)
                if front.startswith('"') and front.endswith('"'): front = front[1:-1]
                if back.startswith('"') and back.endswith('"'): back = back[1:-1]
                
                # Dé-échappement des guillemets doublés (standard CSV)
                front = front.replace('""', '"')
                back = back.replace('""', '"')
                
                # Traitement des chemins d'images
                front = process_media_paths(front, target_dir)
                back = process_media_paths(back, target_dir)
                
                # Ajout des images à Anki
                add_images_from_text(back, target_dir)
                add_images_from_text(front, target_dir)
                
                # Vérification finale : carte vide ?
                if not front.strip() and not back.strip():
                    print(f"    ⚠️  Ligne {row_idx} : Carte vide, ignorée")
                    continue
                
                cards.append({
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": {
                        field_names[0]: front,  # Utilise le 1er champ du modèle (peu importe son nom)
                        field_names[1]: back    # Utilise le 2ème champ
                    },
                    "tags": tags.split() if tags else [],
                    "options": {
                        "allowDuplicate": False,
                        "duplicateScope": "deck"
                    }
                })
    
    except Exception as e:
        print(f"    ❌ Erreur lors de la lecture du CSV : {e}")
        return []
    
    return cards

def create_deck_if_needed(deck_name):
    """
    Crée un deck Anki s'il n'existe pas déjà.
    """
    response = request("deckNames")
    if not response: return False
    
    existing_decks = response.get("result", [])
    if deck_name not in existing_decks:
        response = request("createDeck", deck=deck_name)
        if response and response.get("result"):
            print(f"  ✨ Créé le deck : {deck_name}")
            return True
        else:
            print(f"  ❌ Impossible de créer le deck : {deck_name}")
            return False
    else:
        print(f"  ✓ Le deck existe : {deck_name}")
        return True

def add_notes_to_anki(cards):
    """
    Ajoute les cartes (notes) à Anki via AnkiConnect.
    """
    if not cards: return 0
    
    response = request("addNotes", notes=cards)
    if response:
        results = response.get("result", [])
        successful = len([r for r in results if r is not None])
        failed = len([r for r in results if r is None])
        
        print(f"    ✅ {successful} cartes ajoutées")
        if failed > 0:
            print(f"    ⚠️  {failed} cartes ont échoué (doublons ou erreurs)")
        return successful
    return 0

def get_media_folder_for_csv(csv_filename):
    """
    Détermine le dossier média qui correspond au fichier CSV.
    """
    deck_name = csv_filename.replace('.csv', '').replace('-', '::').replace('_', ' ')
    media_subfolder = deck_name.split("::")[-1].lower().replace(" ", "_")
    
    target_path = os.path.join(MEDIA_DIR, media_subfolder)
    if os.path.exists(target_path):
        return media_subfolder
    else:
        # Recherche approximative
        if os.path.exists(MEDIA_DIR):
            for d in os.listdir(MEDIA_DIR):
                if os.path.isdir(os.path.join(MEDIA_DIR, d)):
                    if media_subfolder in d.lower() or d.lower() in media_subfolder:
                        return d
        return media_subfolder

def main():
    test = request("deckNames")
    if not test:
        print("\n❌ AnkiConnect n'est pas accessible. Assurez-vous qu'Anki est ouvert.")
        return
    
    model_name = get_model_name()
    if not model_name: return
    
    # Récupérer les champs du modèle
    field_names = request("modelFieldNames", modelName=model_name)["result"]
    print(f"  📋 Champs du modèle : {field_names}")
    
    if not field_names or len(field_names) < 2:
        print("  ❌ Le modèle doit avoir au moins 2 champs")
        return
    
    csv_files = []
    if os.path.exists(DECKS_DIR):
        csv_files = sorted([f for f in os.listdir(DECKS_DIR) if f.endswith('.csv')])
    
    if not csv_files:
        print(f"\n❌ Aucun fichier CSV trouvé dans {DECKS_DIR}")
        return
    
    print("\n--- FICHIERS CSV DISPONIBLES ---")
    for index, filename in enumerate(csv_files):
        print(f"[{index}] {filename}")
    
    print("\n-----------------------------------")
    user_input = input("Entrez les numéros à importer (séparés par une virgule, ou 'all') : ")
    
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
    
    for csv_filename in target_files:
        csv_path = os.path.join(DECKS_DIR, csv_filename)
        deck_name = csv_filename.replace('.csv', '').replace('-', '::').replace('_', ' ')
        target_dir = get_media_folder_for_csv(csv_filename)
        
        print(f"📥 Import de '{csv_filename}'...")
        print(f"   → Dossier média : {target_dir}")
        
        if not create_deck_if_needed(deck_name): continue
        
        cards = process_csv_for_anki(csv_path, deck_name, target_dir, model_name, field_names)
        if cards:
            total_added += add_notes_to_anki(cards)
            print()
        else:
            print(f"   ⚠️  Aucune carte à importer\n")
    
    print(f"--- Terminé ! {total_added} cartes importées au total ---")

if __name__ == "__main__":
    main()
