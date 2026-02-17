#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import shutil
import html
import re
from utils import slugify, anki_connect_request

# --- CONFIGURATION ---
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, "decks")
MEDIA_REPO_DIR = os.path.join(BASE_DIR, "media")

# Paths specific to the user's Anki installation
ANKI_USER_PROFILE = "Utilisateur 1"
ANKI_MEDIA_PATH = os.path.expanduser(f"~/Library/Application Support/Anki2/{ANKI_USER_PROFILE}/collection.media")

def copy_media_files(source_text, media_subfolder):
    """
    Cherche les références aux médias dans le texte.
    Les copie du dossier Anki vers le repo.
    Retourne le texte modifié avec les nouveaux chemins relatifs.
    """
    target_dir = os.path.join(MEDIA_REPO_DIR, media_subfolder)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    modified_text = source_text
    
    # Regex pour trouver les images (src="nomfichier.ext")
    image_pattern = r'src=["\']([^"\']+\.(jpg|jpeg|png|gif|svg))["\']'
    matches = re.findall(image_pattern, source_text, re.IGNORECASE)
    
    for match in matches:
        filename = match[0]
        anki_file_path = os.path.join(ANKI_MEDIA_PATH, filename)
        
        if os.path.exists(anki_file_path):
            # Copier le fichier
            repo_file_path = os.path.join(target_dir, filename)
            try:
                shutil.copy2(anki_file_path, repo_file_path)
                print(f"  📸 Copié : {filename}")
                
                # Update path in text to be relative for the repo
                # ../media/subfolder/image.jpg
                new_relative_path = f"../media/{media_subfolder}/{filename}"
                
                # Replace with both quote types to be safe
                modified_text = modified_text.replace(f'src="{filename}"', f'src="{new_relative_path}"')
                modified_text = modified_text.replace(f"src='{filename}'", f"src='{new_relative_path}'")
                
            except Exception as e:
                print(f"  ⚠️  Erreur copie {filename}: {e}")
        else:
            print(f"  ⚠️  Média introuvable : {filename}")
            
    return modified_text

def export_deck(deck_name):
    """Exporte un deck spécifique en CSV + média."""
    print(f"📦 Export de '{deck_name}'...")
    
    # 1. Determine media subfolder
    # Ex: "PTSI::Maths" -> "maths"
    # Ex: "Vocabulaire" -> "vocabulaire"
    parts = deck_name.split("::")
    media_subfolder = slugify(parts[-1])
    
    # 2. Determine file path
    if len(parts) == 1:
        subject = "divers"
        safe_filename = slugify(parts[0])
    else:
        subject = slugify(parts[0])
        safe_filename = "_".join([slugify(p) for p in parts[1:]])
        
    subject_dir = os.path.join(OUTPUT_DIR, subject)
    if not os.path.exists(subject_dir):
        os.makedirs(subject_dir)
        
    csv_filename = os.path.join(subject_dir, f"{safe_filename}.csv")
    
    # 3. Fetch notes from Anki
    find_notes = anki_connect_request("findNotes", query=f'"deck:{deck_name}"')
    if not find_notes:
        return
        
    notes_info = anki_connect_request("notesInfo", notes=find_notes["result"])
    if not notes_info:
        return

    # 4. Write to CSV
    try:
        with open(csv_filename, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            count = 0
            
            for note in notes_info["result"]:
                fields_values = []
                
                # Process fields
                for f_obj in note["fields"].values():
                    raw_value = f_obj["value"]
                    clean_value = html.unescape(raw_value)
                    
                    # Copy media and update paths
                    minified_value = copy_media_files(clean_value, media_subfolder)
                    fields_values.append(minified_value)
                
                # Process tags
                tags = " ".join(note["tags"])
                fields_values.append(tags)
                
                writer.writerow(fields_values)
                count += 1
                
        print(f"✅ OK ({count} cartes)\n")
        
    except Exception as e:
        print(f"❌ ERREUR écriture CSV : {e}\n")

def main():
    print("="*60)
    print("📤 EXPORT DECKS + MÉDIAS")
    print("="*60)
    
    # Get deck list
    response = anki_connect_request("deckNames")
    if not response:
        return
        
    all_decks = response["result"]
    
    print("\n--- DECKS DISPONIBLES ---")
    for index, name in enumerate(all_decks):
        print(f"[{index}] {name}")
    
    user_input = input("\nEntrez les numéros à exporter (séparés par une virgule, ou 'all') : ")
    
    target_decks = []
    if user_input.lower().strip() in ['all', '']:
        target_decks = all_decks
    else:
        try:
            indices = [int(x.strip()) for x in user_input.split(",")]
            target_decks = [all_decks[i] for i in indices if 0 <= i < len(all_decks)]
        except ValueError:
            print("[ERREUR] Saisie invalide.")
            return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"\nDébut de l'export pour {len(target_decks)} deck(s)...\n")
    
    for deck in target_decks:
        export_deck(deck)
        
    print("="*60)
    print("Terminé ! N'oublie pas : git add . && git commit && git push")

if __name__ == "__main__":
    main()
