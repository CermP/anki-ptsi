#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import re
import sys
import base64
from typing import List, Dict, Any, Optional
from utils import anki_connect_request

# --- CONFIGURATION ---
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DECKS_DIR = os.path.join(BASE_DIR, "decks")
MEDIA_DIR = os.path.join(BASE_DIR, "media")

def get_anki_model() -> Optional[str]:
    """Récupère le premier modèle disponible."""
    response = anki_connect_request("modelNames")
    if not response:
        return None
        
    models = response.get("result", [])
    if not models:
        print("  ❌ Aucun modèle trouvé dans Anki")
        return None
        
    # Prefer 'Basic' if available, otherwise first one
    chosen = models[1] if len(models) > 1 and "Basic" in models else models[0]
    print(f"  📋 Utilisation du modèle : {chosen}")
    return chosen

def get_model_fields(model_name: str) -> Optional[List[str]]:
    """Récupère les champs du modèle."""
    response = anki_connect_request("modelFieldNames", modelName=model_name)
    if not response:
        return None
        
    fields = response.get("result", [])
    if fields:
        print(f"  📝 Champs : {', '.join(fields)}")
        return fields
        
    print(f"  ❌ Impossible de récupérer les champs de {model_name}")
    return None

def store_media_file(filename: str, subfolder: str) -> bool:
    """Envoie un fichier média à Anki."""
    # Check in subfolder first, then root
    filepath = os.path.join(MEDIA_DIR, subfolder, filename)
    if not os.path.exists(filepath):
        filepath = os.path.join(MEDIA_DIR, filename)
        if not os.path.exists(filepath):
            return False
            
    try:
        with open(filepath, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
            
        anki_connect_request("storeMediaFile", filename=filename, data=data)
        return True
    except Exception:
        return False

def process_text_images(text: str, subfolder: str) -> str:
    """
    1. Trouve les images src="..." dans le texte.
    2. Les envoie à Anki.
    3. Retroune le texte avec les chemins corrigés pour Anki (src="image.jpg").
    """
    # Clean quotes
    text = text.replace('""', '"')
    
    # Extract images
    # Supports <img src="../media/sub/image.jpg"> and src="image.jpg"
    matches = re.findall(r'src="([^"]+)"', text)
    
    for match in matches:
        if match.startswith('http'):
            continue
            
        filename = os.path.basename(match)
        store_media_file(filename, subfolder)
        
    # Fix paths for Anki: src="../media/sub/image.jpg" -> src="image.jpg"
    text = re.sub(r'src="[^"]*/([^"/]+)"', r'src="\1"', text)
    
    return text

def parse_csv_file(csv_path: str, deck_name: str, subfolder: str, model_name: str, fields: List[str]) -> List[Dict[str, Any]]:
    """Lit le CSV et retourne une liste de notes pour Anki."""
    notes = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            
            for row in reader:
                if len(row) < 2: 
                    continue
                    
                front = row[0].strip()
                back = row[1].strip()
                tags = row[2].strip().split() if len(row) > 2 else []
                
                # Process images
                front = process_text_images(front, subfolder)
                back = process_text_images(back, subfolder)
                
                if not front and not back:
                    continue
                    
                note = {
                    "deckName": deck_name,
                    "modelName": model_name,
                    "fields": {
                        fields[0]: front,
                        fields[1]: back
                    },
                    "tags": tags,
                    "options": {
                        "allowDuplicate": False,
                        "duplicateScope": "deck"
                    }
                }
                notes.append(note)
                
    except Exception as e:
        print(f"    ❌ Erreur CSV {os.path.basename(csv_path)}: {e}")
        return []
        
    return notes

def import_file(csv_path: str, model_name: str, field_names: List[str]) -> None:
    """Importe un fichier CSV spécifique."""
    filename = os.path.basename(csv_path)
    deck_name = filename.replace('.csv', '').replace('-', '::').replace('_', ' ')
    
    # Guess media subfolder from filename
    subfolder = filename.replace('.csv', '').lower().replace(" ", "_").replace("-", "_")
    
    print(f"\n📥 Import de '{filename}' vers '{deck_name}'...")
    
    # Create deck if needed
    anki_connect_request("createDeck", deck=deck_name)
    
    notes = parse_csv_file(csv_path, deck_name, subfolder, model_name, field_names)
    
    if notes:
        response = anki_connect_request("addNotes", notes=notes)
        added = len([r for r in response.get("result", []) if r is not None]) if response else 0
        print(f"   ✅ {added} cartes importées.")
    else:
        print("   ⚠️  Aucune carte importée.")

def interactive_mode(model_name: str, field_names: List[str]) -> None:
    """Mode interactif pour choisir les fichiers."""
    csv_files = []
    for root, _, files in os.walk(DECKS_DIR):
        for f in files:
            if f.endswith('.csv'):
                csv_files.append(os.path.join(root, f))
                
    csv_files.sort()
    
    if not csv_files:
        print(f"\n❌ Aucun fichier CSV trouvé dans {DECKS_DIR}")
        return

    print("\n--- FICHIERS DISPONIBLES ---")
    pad = len(str(len(csv_files)))
    for i, path in enumerate(csv_files):
        rel_path = os.path.relpath(path, DECKS_DIR)
        print(f"[{str(i).zfill(pad)}] {rel_path}")
        
    selection = input("\nEntrez les numéros (ex: 1, 3) ou 'all' : ")
    
    to_import = []
    if selection.lower().strip() in ['all', '']:
        to_import = csv_files
    else:
        try:
            indices = [int(x.strip()) for x in selection.split(",")]
            to_import = [csv_files[i] for i in indices if 0 <= i < len(csv_files)]
        except ValueError:
            print("[ERREUR] Saisie invalide.")
            return

    print(f"\n🚀 Début de l'import pour {len(to_import)} fichier(s)...\n")
    for path in to_import:
        import_file(path, model_name, field_names)

def main() -> None:
    # Check connection
    if not anki_connect_request("version"):
        print("\n❌ AnkiConnect n'est pas accessible. Lancez Anki.")
        return

    model = get_anki_model()
    if not model: return
    
    fields = get_model_fields(model)
    if not fields or len(fields) < 2:
        print("❌ Le modèle doit avoir au moins 2 champs.")
        return

    # Check CLI args
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            import_file(file_path, model, fields)
        else:
            print(f"❌ Fichier introuvable : {file_path}")
    else:
        interactive_mode(model, fields)

if __name__ == "__main__":
    main()
