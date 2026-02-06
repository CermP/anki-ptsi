#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json

# --- CONFIGURATION ---
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BASE_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

print("="*60)
print("📊 GÉNÉRATION DE L'INDEX DES DECKS")
print("="*60)
print(f"📂 Dossier de sortie : {OUTPUT_DIR}")
print()

# Crée le dossier output s'il n'existe pas
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print("ℹ️ Dossier output créé")

# --- COLLECTE DES DECKS ---
def collect_decks():
    decks_by_subject = {}
    
    try:
        files = os.listdir(OUTPUT_DIR)
    except Exception as e:
        print(f"❌ Erreur lecture dossier : {e}")
        return decks_by_subject
    
    apkg_files = [f for f in files if f.endswith('.apkg')]
    print(f"🔍 Fichiers .apkg trouvés : {len(apkg_files)}")
    
    for filename in sorted(apkg_files):
        try:
            # Parse le nom : Matiere-Titre.apkg
            base = filename.replace('.apkg', '')
            
            if '-' in base:
                parts = base.split('-', 1)
                subject = parts[0].capitalize()
                title = parts[1].replace('_', ' ')
            else:
                subject = "Autres"
                title = base.replace('_', ' ')
            
            # Taille du fichier
            filepath = os.path.join(OUTPUT_DIR, filename)
            size_bytes = os.path.getsize(filepath)
            
            if size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            # Ajout au dictionnaire
            if subject not in decks_by_subject:
                decks_by_subject[subject] = []
            
            decks_by_subject[subject].append({
                'name': title,
                'filename': filename,
                'size': size_str
            })
            
            print(f"   ✅ {subject} : {title} ({size_str})")
            
        except Exception as e:
            print(f"   ⚠️ Erreur pour {filename}: {e}")
    
    return decks_by_subject

# --- GÉNÉRATION JSON ---
def save_json(data):
    path = os.path.join(OUTPUT_DIR, 'decks.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON créé : decks.json")
    except Exception as e:
        print(f"\n❌ Erreur JSON : {e}")

# --- GÉNÉRATION HTML ---
def save_html(data):
    total_decks = sum(len(d) for d in data.values()) if data else 0
    total_subjects = len(data) if data else 0
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decks Anki PTSI</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #2e3440;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #3b4252;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #5e81ac 0%, #8fbcbb 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 700; }}
        .subtitle {{ font-size: 1.1rem; opacity: 0.9; }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        .stat-number {{ font-size: 2rem; font-weight: 700; color: white; }}
        .stat-label {{ font-size: 0.9rem; opacity: 0.9; }}
        .content {{ padding: 2rem; }}
        .subject-section {{ margin-bottom: 2.5rem; }}
        .subject-title {{
            font-size: 1.5rem;
            color: #e5e9f0;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #d8dee9;
            font-weight: 600;
        }}
        .deck-list {{ display: flex; flex-direction: column; gap: 0.75rem; }}
        .deck-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 1.25rem;
            background: #f8f9fa;
            border-radius: 10px;
            transition: all 0.2s ease;
            border: 2px solid transparent;
        }}
        .deck-item:hover {{
            background: #81a1c1;
            border-color: #88c0d0;
            transform: translateX(5px);
        }}
        .deck-info {{ flex: 1; }}
        .deck-name {{ font-weight: 600; color: #2d3748; margin-bottom: 0.25rem; }}
        .deck-size {{ font-size: 0.875rem; color: #718096; }}
        .download-btn {{
            background: #bf616a;
            color: white;
            padding: 0.6rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .download-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .empty-state {{
            text-align: center;
            padding: 3rem 2rem;
            color: #b48ead;
        }}
        footer {{
            background: #4c566a;
            padding: 2rem;
            text-align: center;
            color: #b48ead;
            border-top: 1px solid #d8dee9;
        }}
        footer a {{ color: #88c0d0; text-decoration: none; font-weight: 600; }}
        footer a:hover {{ text-decoration: underline; }}
        @media (max-width: 600px) {{
            h1 {{ font-size: 1.8rem; }}
            .content {{ padding: 1.5rem; }}
            .deck-item {{ flex-direction: column; align-items: flex-start; gap: 1rem; }}
            .download-btn {{ width: 100%; text-align: center; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Decks Anki PTSI</h1>
            <p class="subtitle">Téléchargez les packets, un click et c'est dans Anki !</p>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number">{total_decks}</div>
                    <div class="stat-label">Decks disponibles</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{total_subjects}</div>
                    <div class="stat-label">Matières</div>
                </div>
            </div>
        </header>
        <div class="content">'''
    
    if not data or total_decks == 0:
        html += '''
            <div class="empty-state">
                <h2>📦 Aucun deck disponible</h2>
                <p>Les decks seront générés au prochain push.</p>
            </div>'''
    else:
        for subject in sorted(data.keys()):
            html += f'''
            <div class="subject-section">
                <h2 class="subject-title">{subject}</h2>
                <div class="deck-list">'''
            
            for deck in data[subject]:
                html += f'''
                    <div class="deck-item">
                        <div class="deck-info">
                            <div class="deck-name">{deck['name']}</div>
                            <div class="deck-size">{deck['size']}</div>
                        </div>
                        <a href="{deck['filename']}" class="download-btn" download>⬇️ Télécharger</a>
                    </div>'''
            
            html += '''
                </div>
            </div>'''
    
    html += '''
        </div>
        <footer>
            <p><a href="https://github.com/CermP/anki-ptsi" target="_blank">CermP/anki-ptsi</a> sur GitHub</p>
            <p style="margin-top: 0.5rem;">🤝 Contributions bienvenues -> rendez-vous sur github pour contribuer !</p>
        </footer>
    </div>
</body>
</html>'''
    
    path = os.path.join(OUTPUT_DIR, 'index.html')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ HTML créé : index.html")
    except Exception as e:
        print(f"❌ Erreur HTML : {e}")

# --- MAIN ---
if __name__ == "__main__":
    decks = collect_decks()
    save_json(decks)
    save_html(decks)
    
    print("\n" + "="*60)
    if decks:
        total = sum(len(d) for d in decks.values())
        print(f"✨ SUCCÈS : {total} deck(s) dans {len(decks)} matière(s)")
    else:
        print("ℹ️ Aucun deck trouvé (mais index généré quand même)")
    print("="*60)
