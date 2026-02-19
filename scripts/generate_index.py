#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from datetime import date
from urllib.parse import quote
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader

# --- CONFIGURATION ---
SCRIPT_PATH = Path(__file__).resolve()
BASE_DIR = SCRIPT_PATH.parent.parent
OUTPUT_DIR = BASE_DIR / "docs"

BASE_URL = "https://cermp.github.io/anki-ptsi/"

def get_file_size_str(filepath: Path) -> str:
    """Retourne la taille du fichier formatée (KB/MB)."""
    size_bytes = filepath.stat().st_size
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"

def collect_decks_info() -> Dict[str, List[Dict[str, str]]]:
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

def save_json(data: Dict[str, List[Dict[str, str]]]) -> None:
    """Sauvegarde les données dans decks.json."""
    json_path = OUTPUT_DIR / 'decks.json'
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON créé : {json_path.name}")
    except Exception as e:
        print(f"❌ Erreur JSON : {e}")

def save_sitemap(data: Dict[str, List[Dict[str, str]]]) -> None:
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

def save_html(data: Dict[str, List[Dict[str, str]]]) -> None:
    """Génère et sauvegarde le fichier decks.html via Jinja2."""
    total_decks = sum(len(d) for d in data.values()) if data else 0
    total_subjects = len(data) if data else 0
    
    env = Environment(loader=FileSystemLoader(str(SCRIPT_PATH.parent / 'templates')))
    template = env.get_template('decks_template.html')
    
    html_content = template.render(
        data=data,
        total_decks=total_decks,
        total_subjects=total_subjects
    )
    
    html_path = OUTPUT_DIR / 'decks.html'
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML créé : {html_path.name}")
    except Exception as e:
        print(f"❌ Erreur HTML : {e}")

def main() -> None:
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
