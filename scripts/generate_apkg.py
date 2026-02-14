#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import genanki
import csv
import os
import re
import unicodedata

# --- CONFIGURATION AUTOMATIQUE DES CHEMINS ---
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

DECKS_DIR = os.path.join(BASE_DIR, "decks")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"📂 Dossier decks : {DECKS_DIR}")
print(f"📂 Dossier media : {MEDIA_DIR}")
print(f"📂 Dossier output : {OUTPUT_DIR}")
print()

# --- UTILITAIRE ---
def slugify(value):
    """Supprime les accents et caractères spéciaux (identique à l'export)"""
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)

# --- MODÈLE ANKI ---
MODEL_ID = 1607392319
MY_MODEL = genanki.Model(
  MODEL_ID,
  'PTSI Modele Simple',
  fields=[{'name': 'Question'}, {'name': 'Reponse'}],
  templates=[{
      'name': 'Carte 1',
      'qfmt': '{{Question}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{Reponse}}',
  }])

def get_unique_deck_id(deck_name):
    return abs(hash(deck_name)) % (10 ** 8)

def process_csv_file(csv_path, subject_folder):
    """Traite un fichier CSV et génère un .apkg"""
    
    filename = os.path.basename(csv_path)
    base_name = filename.replace('.csv', '')
    
    # Construction du nom du deck pour Anki
    # Si le fichier commence par le nom de la matière, on le supprime
    if base_name.lower().startswith(subject_folder.lower() + '-'):
        clean_name = base_name[len(subject_folder)+1:]  # Enlève "Maths-"
    elif base_name.lower().startswith(subject_folder.lower() + '_'):
        clean_name = base_name[len(subject_folder)+1:]  # Enlève "Maths_"
    else:
        clean_name = base_name
    
    # Nom du deck dans Anki : Matière::Titre
    deck_name = f"{subject_folder}::{clean_name.replace('_', ' ')}"
    
    # Nom du fichier .apkg de sortie
    output_filename = f"{subject_folder}-{clean_name}.apkg"
    
    # CALCUL DU DOSSIER MEDIA
    # On utilise le slug du dernier élément du nom du deck
    last_part = deck_name.split('::')[-1]
    media_subfolder = slugify(last_part)
    
    print(f"🔨 Traitement : {filename}")
    print(f"   📦 Deck Anki : {deck_name}")
    print(f"   🖼️  Dossier média : media/{media_subfolder}/")
    print(f"   💾 Fichier sortie : {output_filename}")
    
    deck = genanki.Deck(get_unique_deck_id(deck_name), deck_name)
    media_files_to_include = []
    card_count = 0

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                if len(row) < 2:
                    continue
                
                front, back = row[0], row[1]
                # Nettoyage des guillemets doublés du CSV
                front = front.replace('""', '"').strip('"')
                back = back.replace('""', '"').strip('"')

                # --- ÉTAPE CRUCIALE : NETTOYAGE DES CHEMINS POUR L'AFFICHAGE DANS ANKI ---
                # On transforme <img src="../media/si/photo.jpg"> en <img src="photo.jpg">
                # Sinon Anki cherche un dossier qui n'existe pas sur le téléphone/ordinateur
                front = re.sub(r'src="[^"]*/([^"/]+)"', r'src="\1"', front)
                back = re.sub(r'src="[^"]*/([^"/]+)"', r'src="\1"', back)

                # Création de la note avec le texte nettoyé
                note = genanki.Note(model=MY_MODEL, fields=[front, back])
                deck.add_note(note)
                card_count += 1

                # --- COLLECTE DES IMAGES POUR LE PAQUET APKG ---
                image_refs = re.findall(r'src="([^"]+)"', row[0] + row[1]) 
                for img_ref in image_refs:
                    img_name = os.path.basename(img_ref)
                    
                    # Cherche l'image dans le dossier média correspondant
                    full_img_path = os.path.join(MEDIA_DIR, media_subfolder, img_name)
                    
                    if os.path.exists(full_img_path):
                        if full_img_path not in media_files_to_include:
                            media_files_to_include.append(full_img_path)
                    else:
                        print(f"      ⚠️ Image manquante : {img_name} (cherchée dans media/{media_subfolder}/)")

        # Génération du fichier .apkg final
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        package = genanki.Package(deck)
        package.media_files = media_files_to_include
        package.write_to_file(output_path)
        
        print(f"   ✅ Créé : {card_count} cartes, {len(media_files_to_include)} images")
        print()
        return True
        
    except Exception as e:
        print(f"   ❌ ERREUR : {e}")
        print()
        return False

# --- LANCEMENT ---
if __name__ == "__main__":
    print("="*60)
    print("🚀 GÉNÉRATION DES PAQUETS ANKI (.apkg)")
    print("="*60)
    print()
    
    total_processed = 0
    total_success = 0
    total_errors = 0
    
    # Parcours récursif du dossier decks/
    for root, dirs, files in os.walk(DECKS_DIR):
        # Détermine la matière à partir du dossier
        relative_path = os.path.relpath(root, DECKS_DIR)
        
        if relative_path == '.':
            subject_folder = 'Divers'
        else:
            # Prend le premier niveau de dossier comme matière
            subject_folder = relative_path.split(os.sep)[0]
        
        # Traite tous les CSV du dossier
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if csv_files:
            print(f"📁 Matière : {subject_folder} ({len(csv_files)} fichier(s))")
            print()
            
            for csv_file in csv_files:
                total_processed += 1
                csv_path = os.path.join(root, csv_file)
                
                if process_csv_file(csv_path, subject_folder):
                    total_success += 1
                else:
                    total_errors += 1
    
    print("="*60)
    print(f"✨ RÉSUMÉ")
    print("="*60)
    print(f"📊 Fichiers traités : {total_processed}")
    print(f"✅ Succès : {total_success}")
    print(f"❌ Erreurs : {total_errors}")
    print()
    
    if total_success > 0:
        print(f"🎉 {total_success} paquet(s) .apkg généré(s) avec succès !")
    else:
        print("⚠️ Aucun paquet généré.")
