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

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
    print("ℹ️ Dossier output créé")

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
            base = filename.replace('.apkg', '')
            
            if '-' in base:
                parts = base.split('-', 1)
                subject = parts[0].capitalize()
                title = parts[1].replace('_', ' ')
            else:
                subject = "Autres"
                title = base.replace('_', ' ')
            
            filepath = os.path.join(OUTPUT_DIR, filename)
            size_bytes = os.path.getsize(filepath)
            
            if size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
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

def save_json(data):
    path = os.path.join(OUTPUT_DIR, 'decks.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON créé : decks.json")
    except Exception as e:
        print(f"\n❌ Erreur JSON : {e}")

def save_html(data):
    total_decks = sum(len(d) for d in data.values()) if data else 0
    total_subjects = len(data) if data else 0
    
    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="google-site-verification" content="DmmybIY5FSzQJMfHe_74H2ciJW4PxvPLA-KXHtOE3_I" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decks Anki PTSI - CermP</title>
    <style>
        /* ===== NORD THEME PALETTE ===== */
        :root {{
            /* Polar Night (fonds sombres) */
            --nord0: #2e3440;  /* Fond principal */
            --nord1: #3b4252;  /* Cartes/panels */
            --nord2: #434c5e;  /* Hover/borders */
            --nord3: #4c566a;  /* Séparateurs */
            
            /* Snow Storm (textes clairs) */
            --nord4: #d8dee9;  /* Texte principal */
            --nord5: #e5e9f0;  /* Texte subtil */
            --nord6: #eceff4;  /* Texte très clair */
            
            /* Frost (accents bleus) */
            --nord7: #8fbcbb;  /* Bleu-vert (primaire) */
            --nord8: #88c0d0;  /* Bleu clair */
            --nord9: #81a1c1;  /* Bleu moyen */
            --nord10: #5e81ac; /* Bleu foncé */
            
            /* Aurora (feedback/états) */
            --nord11: #bf616a; /* Rouge (erreur) */
            --nord12: #d08770; /* Orange (warning) */
            --nord13: #ebcb8b; /* Jaune */
            --nord14: #a3be8c; /* Vert (succès) */
            --nord15: #b48ead; /* Violet */
        }}
        
        /* ===== RESET & BASE ===== */
        * {{ 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--nord0);
            color: var(--nord4);
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
        }}
        
        /* ===== HEADER ===== */
        header {{
            background: var(--nord1);
            border-radius: 16px;
            padding: 3rem 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            border: 1px solid var(--nord2);
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--nord8), var(--nord7));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -0.02em;
        }}
        
        .subtitle {{
            font-size: 1.1rem;
            color: var(--nord4);
            opacity: 0.8;
        }}
        
        /* ===== STATS ===== */
        .stats {{
            display: flex;
            justify-content: center;
            gap: 3rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 1rem 2rem;
            background: var(--nord0);
            border-radius: 12px;
            border: 1px solid var(--nord3);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--nord7);
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            color: var(--nord4);
            opacity: 0.7;
            margin-top: 0.25rem;
        }}
        
        /* ===== CONTENT ===== */
        .content {{
            display: grid;
            gap: 2rem;
        }}
        
        /* ===== SUBJECT SECTION ===== */
        .subject-section {{
            background: var(--nord1);
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid var(--nord2);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease;
        }}
        
        .subject-section:hover {{
            transform: translateY(-2px);
        }}
        
        .subject-title {{
            font-size: 1.5rem;
            color: var(--nord8);
            margin-bottom: 1.25rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--nord3);
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .subject-icon {{
            width: 10px;
            height: 10px;
            background: var(--nord7);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 10px var(--nord7);
        }}
        
        /* ===== DECK LIST ===== */
        .deck-list {{
            display: grid;
            gap: 0.75rem;
        }}
        
        .deck-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.1rem 1.5rem;
            background: var(--nord0);
            border-radius: 10px;
            transition: all 0.2s ease;
            border: 1px solid var(--nord2);
        }}
        
        .deck-item:hover {{
            background: var(--nord2);
            border-color: var(--nord7);
            transform: scale(1.025);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }}
        
        .deck-info {{
            flex: 1;
        }}
        
        .deck-name {{
            font-weight: 600;
            color: var(--nord6);
            margin-bottom: 0.3rem;
            font-size: 0.95rem;
        }}
        
        .deck-size {{
            font-size: 0.85rem;
            color: var(--nord4);
            opacity: 0.6;
        }}
        
        /* ===== DOWNLOAD BUTTON ===== */
        .download-btn {{
            background: var(--nord7);
            color: var(--nord0);
            padding: 0.7rem 1.6rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 2px 8px rgba(143, 188, 187, 0.3);
        }}
        
        .download-btn:hover {{
            background: var(--nord8);
            transform: scale(1.025);
            box-shadow: 0 4px 16px rgba(136, 192, 208, 0.5);
        }}
        
        .download-btn:active {{
            transform: scale(0.98);
        }}
        
        /* ===== EMPTY STATE ===== */
        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            background: var(--nord1);
            border-radius: 16px;
            border: 1px solid var(--nord2);
        }}
        
        .empty-state h2 {{
            color: var(--nord4);
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .empty-state p {{
            color: var(--nord4);
            opacity: 0.7;
        }}
        
        /* ===== FOOTER ===== */
        footer {{
            margin-top: 3rem;
            text-align: center;
            padding: 2rem;
            background: var(--nord1);
            border-radius: 16px;
            border: 1px solid var(--nord2);
            color: var(--nord4);
        }}
        
        footer a {{
            color: var(--nord8);
            text-decoration: none;
            font-weight: 600;
            transition: color 0.2s ease;
        }}
        
        footer a:hover {{
            color: var(--nord7);
            text-decoration: underline;
        }}
        
        /* ===== RESPONSIVE ===== */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            header {{
                padding: 2rem 1.5rem;
            }}
            
            .stats {{
                gap: 1.5rem;
            }}
            
            .stat-item {{
                padding: 0.75rem 1.5rem;
            }}
            
            .deck-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }}
            
            .download-btn {{
                width: 100%;
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Decks Anki PTSI</h1>
            <p class="subtitle">Téléchargez les packets, un clic et c'est dans Anki !</p>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{total_decks}</span>
                    <span class="stat-label">Decks disponibles</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_subjects}</span>
                    <span class="stat-label">Matières</span>
                </div>
            </div>
        </header>
        
        <div class="content">'''
    
    if not data or total_decks == 0:
        html += '''
            <div class="empty-state">
                <h2>📦 Aucun deck disponible</h2>
                <p>Les decks seront générés au prochain push sur GitHub.</p>
            </div>'''
    else:
        for subject in sorted(data.keys()):
            html += f'''
            <div class="subject-section">
                <h2 class="subject-title">
                    <span class="subject-icon"></span>
                    {subject}
                </h2>
                <div class="deck-list">'''
            
            for deck in data[subject]:
                html += f'''
                    <div class="deck-item">
                        <div class="deck-info">
                            <div class="deck-name">{deck['name']}</div>
                            <div class="deck-size">{deck['size']}</div>
                        </div>
                        <a href="{deck['filename']}" class="download-btn" download>
                            <span>📥</span>
                            <span>Télécharger</span>
                        </a>
                    </div>'''
            
            html += '''
                </div>
            </div>'''
    
    html += '''
        </div>
        
        <footer>
            <p>Projet open source : <a href="https://github.com/CermP/anki-ptsi" target="_blank" rel="noopener">CermP/anki-ptsi</a></p>
            <p style="margin-top: 0.5rem; opacity: 0.7;">🤝 Contributions bienvenues sur GitHub !</p>
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

if __name__ == "__main__":
    decks = collect_decks()
    save_json(decks)
    save_html(decks)
    
    print("\n" + "="*60)
    if decks:
        total = sum(len(d) for d in decks.values())
        print(f"✨ SUCCÈS : {total} deck(s) dans {len(decks)} matières")
    else:
        print("ℹ️ Aucun deck trouvé (mais index généré quand même)")
    print("="*60)
