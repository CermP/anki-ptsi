#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
import re
import sys
import genanki
from typing import List, Tuple
from utils import slugify

# --- CONFIGURATION ---
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DECKS_DIR = os.path.join(BASE_DIR, "decks")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")

# --- ANKI MODEL ---
MODEL_ID = 1607392319
PTSI_MODEL = genanki.Model(
    MODEL_ID,
    'PTSI Modele Simple',
    fields=[{'name': 'Question'}, {'name': 'Reponse'}],
    templates=[{
        'name': 'Carte 1',
        'qfmt': '{{Question}}',
        'afmt': '{{FrontSide}}<hr id="answer">{{Reponse}}',
    }]
)

def get_unique_deck_id(deck_name: str) -> int:
    """Génère un ID unique pour le deck basé sur son nom."""
    return abs(hash(deck_name)) % (10 ** 8)

def clean_deck_name(base_name: str, subject_folder: str) -> str:
    """Nettoie le nom du fichier pour obtenir le nom du titre."""
    prefix_dash = f"{subject_folder.lower()}-"
    prefix_underscore = f"{subject_folder.lower()}_"
    
    name_lower = base_name.lower()
    if name_lower.startswith(prefix_dash):
        return base_name[len(prefix_dash):]
    elif name_lower.startswith(prefix_underscore):
        return base_name[len(prefix_underscore):]
    
    return base_name

def extract_media_refs(text: str) -> List[str]:
    """Extrait les références d'images src="..."."""
    return re.findall(r'src="([^"]+)"', text)

def clean_media_paths(text: str) -> str:
    """Nettoie les chemins d'images pour Anki."""
    # Transforme <img src="../media/si/photo.jpg"> en <img src="photo.jpg">
    return re.sub(r'src="[^"]*/([^"/]+)"', r'src="\1"', text)

def process_csv_rows(csv_path: str) -> Tuple[List[genanki.Note], List[str]]:
    """Lit un fichier CSV et génère des notes."""
    notes = []
    media_refs = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                if len(row) < 2:
                    continue
                
                front, back = row[0], row[1]
                # Clean quoted quotes
                front = front.replace('""', '"').strip('"')
                back = back.replace('""', '"').strip('"')
                
                # Collect media references BEFORE cleaning paths
                media_refs.extend(extract_media_refs(front + back))
                
                # Clean paths for Anki
                front = clean_media_paths(front)
                back = clean_media_paths(back)
                
                note = genanki.Note(model=PTSI_MODEL, fields=[front, back])
                notes.append(note)
                
    except Exception as e:
        print(f"   ❌ Erreur lecture CSV {os.path.basename(csv_path)}: {e}")
        return [], []
        
    return notes, media_refs

def find_media_files(media_refs: List[str], media_subfolder: str) -> List[str]:
    """Trouve les fichiers images correspondants dans media/."""
    create_package_media = []
    
    for img_ref in media_refs:
        img_name = os.path.basename(img_ref)
        full_img_path = os.path.join(MEDIA_DIR, media_subfolder, img_name)
        
        if os.path.exists(full_img_path):
            if full_img_path not in create_package_media:
                create_package_media.append(full_img_path)
        else:
            print(f"      ⚠️ Image manquante : {img_name} (cherchée dans media/{media_subfolder}/)")
            
    return create_package_media

def generate_deck_package(csv_path: str, subject_folder: str) -> bool:
    """Génère un paquet .apkg à partir d'un fichier CSV."""
    filename = os.path.basename(csv_path)
    base_name = filename.replace('.csv', '')
    
    clean_name = clean_deck_name(base_name, subject_folder)
    deck_name = f"{subject_folder}::{clean_name.replace('_', ' ')}"
    output_filename = f"{subject_folder}-{clean_name}.apkg"
    
    # Media subfolder relies on the last part of the deck name
    last_part = deck_name.split('::')[-1]
    media_subfolder = slugify(last_part)
    
    print(f"🔨 Traitement : {filename}")
    print(f"   📦 Deck Anki : {deck_name}")
    
    notes, media_refs = process_csv_rows(csv_path)
    if not notes:
        return False

    deck = genanki.Deck(get_unique_deck_id(deck_name), deck_name)
    for note in notes:
        deck.add_note(note)
        
    media_files = find_media_files(media_refs, media_subfolder)
    
    # Save package
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    package = genanki.Package(deck)
    package.media_files = media_files
    
    try:
        package.write_to_file(output_path)
        print(f"   ✅ Créé : {len(notes)} cartes, {len(media_files)} images")
        print()
        return True
    except Exception as e:
        print(f"   ❌ Erreur écriture .apkg : {e}")
        return False

def main() -> None:
    print("="*60)
    print("🚀 GÉNÉRATION DES PAQUETS ANKI (.apkg)")
    print("="*60)
    print()
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    stats = {'processed': 0, 'success': 0, 'errors': 0}
    
    for root, _, files in os.walk(DECKS_DIR):
        relative_path = os.path.relpath(root, DECKS_DIR)
        
        if relative_path == '.':
            subject_folder = 'Divers'
        else:
            subject_folder = relative_path.split(os.sep)[0]
            
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if csv_files:
            print(f"📁 Matière : {subject_folder} ({len(csv_files)} fichier(s))")
            print()
            
            for csv_file in csv_files:
                stats['processed'] += 1
                csv_path = os.path.join(root, csv_file)
                
                if generate_deck_package(csv_path, subject_folder):
                    stats['success'] += 1
                else:
                    stats['errors'] += 1
                    
    print("="*60)
    print(f"✨ RÉSUMÉ")
    print("="*60)
    print(f"📊 Fichiers traités : {stats['processed']}")
    print(f"✅ Succès : {stats['success']}")
    print(f"❌ Erreurs : {stats['errors']}")
    print()
    
    if stats['success'] == 0 and stats['processed'] > 0:
        print("⚠️ Aucun paquet généré.")

if __name__ == "__main__":
    main()
