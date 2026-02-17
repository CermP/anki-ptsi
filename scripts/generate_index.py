#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import date
from urllib.parse import quote
from pathlib import Path

# --- CONFIGURATION ---
SCRIPT_PATH = Path(__file__).resolve()
BASE_DIR = SCRIPT_PATH.parent.parent
OUTPUT_DIR = BASE_DIR / "docs"

BASE_URL = "https://cermp.github.io/anki-ptsi/"

def get_file_size_str(filepath):
    """Retourne la taille du fichier formatée (KB/MB)."""
    size_bytes = filepath.stat().st_size
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"

def collect_decks_info():
    """Parcourt le dossier docs/ pour trouver les fichiers .apkg."""
    decks_by_subject = {}
    
    if not OUTPUT_DIR.exists():
        print(f"❌ Dossier introuvable : {OUTPUT_DIR}")
        return {}

    apkg_files = sorted(OUTPUT_DIR.glob("*.apkg"))
    print(f"🔍 Fichiers .apkg trouvés : {len(apkg_files)}")
    
    for filepath in apkg_files:
        filename = filepath.name
        base_name = filepath.stem
        
        # Parse subject from filename "Subject-Title.apkg"
        if '-' in base_name:
            parts = base_name.split('-', 1)
            subject = parts[0].capitalize()
            title = parts[1].replace('_', ' ')
        else:
            subject = "Autres"
            title = base_name.replace('_', ' ')
            
        if subject not in decks_by_subject:
            decks_by_subject[subject] = []
            
        deck_info = {
            'name': title,
            'filename': filename,
            'size': get_file_size_str(filepath),
            'date': date.fromtimestamp(filepath.stat().st_mtime).strftime("%d/%m/%Y"),
            'url': quote(filename)
        }
        
        decks_by_subject[subject].append(deck_info)
        print(f"   ✅ {subject} : {title} ({deck_info['size']})")
        
    return decks_by_subject

def save_json(data):
    """Sauvegarde les données dans decks.json."""
    json_path = OUTPUT_DIR / 'decks.json'
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON créé : {json_path.name}")
    except Exception as e:
        print(f"❌ Erreur JSON : {e}")

def save_sitemap(data):
    """Génère le sitemap.xml."""
    today = date.today().isoformat()
    
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{BASE_URL}</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '  </url>',
        '  <url>',
        f'    <loc>{BASE_URL}decks.html</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>daily</changefreq>',
        '  </url>'
    ]
    
    if data:
        for deck_list in data.values():
            for deck in deck_list:
                xml_lines.extend([
                    '  <url>',
                    f'    <loc>{BASE_URL}{deck["url"]}</loc>',
                    f'    <lastmod>{today}</lastmod>',
                    '  </url>'
                ])
                
    xml_lines.append('</urlset>')
    
    sitemap_path = OUTPUT_DIR / 'sitemap.xml'
    try:
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(xml_lines))
        print(f"✅ Sitemap créé : {sitemap_path.name}")
    except Exception as e:
        print(f"❌ Erreur Sitemap : {e}")

def generate_html_content(data):
    """Génère le contenu HTML de la page des decks."""
    total_decks = sum(len(d) for d in data.values()) if data else 0
    total_subjects = len(data) if data else 0
    
    # Header logic
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anki PTSI — Téléchargement des Decks</title>
    <meta name="description" content="Téléchargez les decks Anki pour la PTSI.">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/GlassSurface.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <nav class="glass-navbar">
        <a href="index.html" class="glass-brand">Anki PTSI</a>
        <div class="glass-nav-links">
            <a href="index.html" class="glass-nav-link">Accueil</a>
            <a href="decks.html" class="glass-nav-link active">Decks</a>
            <a href="https://github.com/CermP/anki-ptsi" target="_blank" class="glass-nav-link">GitHub</a>
        </div>
    </nav>

    <header>
        <div class="container hero-content">
            <h1 class="hero-title">Anki PTSI</h1>
            <p class="hero-subtitle">Mémorisez vos cours efficacement.</p>
            
            <div class="search-container">
                <input type="text" id="search-input" class="search-input" placeholder="Rechercher...">
            </div>

            <div class="stats-container">
                <div class="stat-badge"><strong>{total_decks}</strong> Decks</div>
                <div class="stat-badge"><strong>{total_subjects}</strong> Matières</div>
            </div>
        </div>
    </header>

    <div class="container main-content">
'''
    
    if not data:
        html += '<div class="empty-state"><h2>Aucun deck disponible</h2></div>'
    else:
        # No results hidden div
        html += '''<div id="no-results" class="no-results" style="display: none;">
            <h3>Aucun résultat trouvé.</h3>
        </div>'''
        
        for subject in sorted(data.keys()):
            html += f'''
            <section class="subject-section">
                <h2 class="subject-title">{subject}</h2>
                <div class="deck-grid">'''
                
            for deck in data[subject]:
                html += f'''
                    <div class="deck-card">
                        <div class="deck-info">
                            <h3 class="deck-name">{deck['name']}</h3>
                            <div class="deck-meta">
                                <span>{deck['date']}</span>
                                <span>{deck['size']}</span>
                            </div>
                        </div>
                        <a href="{deck['url']}" class="download-btn" download>Télécharger</a>
                    </div>'''
            html += '</div></section>'

    html += '''
    </div>
    <footer>
        <div class="container">
            <p>Projet open source par <a href="https://github.com/CermP/anki-ptsi">CermP</a></p>
        </div>
    </footer>
    <script src="js/main.js"></script>
</body>
</html>'''
    return html

def save_html(data):
    """Sauvegarde le fichier decks.html."""
    html_content = generate_html_content(data)
    html_path = OUTPUT_DIR / 'decks.html'
    
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML créé : {html_path.name}")
    except Exception as e:
        print(f"❌ Erreur HTML : {e}")

def main():
    print("="*60)
    print("📊 GÉNÉRATION INDEX DECKS")
    print("="*60)
    
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)
        
    decks = collect_decks_info()
    
    save_json(decks)
    save_html(decks)
    save_sitemap(decks)
    
    print("\n" + "="*60)
    print("Terminé.")

if __name__ == "__main__":
    main()
