import os
import json
from pathlib import Path
import re

# --- CONFIGURATION AUTOMATIQUE DES CHEMINS ---
SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
BASE_DIR = os.path.dirname(SCRIPT_DIR)

OUTPUT_DIR = os.path.join(BASE_DIR, "output")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- COLLECTE DES DECKS ---
def collect_decks():
    """Parcourt le dossier output et récupère tous les .apkg générés"""
    decks_by_subject = {}
    
    # Vérifier que le dossier existe et contient des fichiers
    if not os.path.exists(OUTPUT_DIR):
        print(f"⚠️ Le dossier {OUTPUT_DIR} n'existe pas")
        return decks_by_subject
    
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.apkg')]
    print(f"🔍 Trouvé {len(files)} fichiers .apkg dans {OUTPUT_DIR}")
    
    for filename in sorted(files):
        print(f"   - Traitement de {filename}")
        
        # Déduit la matière et le nom du deck
        # Format attendu : Matiere-Chapitre.apkg ou matiere-sous_matiere-sujet.apkg
        base_name = filename.replace('.apkg', '')
        
        # Cherche le pattern "Matiere-" au début
        parts = base_name.split('-', 1)  # Split seulement sur le premier tiret
        
        if len(parts) >= 2:
            subject = parts[0].strip().capitalize()
            deck_title = parts[1].strip()
        else:
            # Si pas de tiret, utilise le nom complet
            subject = "Autres"
            deck_title = base_name
        
        # Reconstitue un nom lisible
        deck_name = deck_title.replace('_', ' ')
        
        # Calcul de la taille du fichier
        file_path = os.path.join(OUTPUT_DIR, filename)
        try:
            file_size = os.path.getsize(file_path)
            
            # Conversion en KB/MB
            if file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            if subject not in decks_by_subject:
                decks_by_subject[subject] = []
            
            decks_by_subject[subject].append({
                'name': deck_name,
                'filename': filename,
                'size': size_str,
                'size_bytes': file_size
            })
            print(f"      → Ajouté dans la catégorie '{subject}' : {deck_name}")
            
        except Exception as e:
            print(f"   ⚠️ Erreur lors de la lecture de {filename}: {e}")
            continue
    
    return decks_by_subject

# --- GÉNÉRATION DU JSON ---
def generate_json(decks_data):
    """Génère un fichier JSON avec la liste des decks"""
    json_path = os.path.join(OUTPUT_DIR, 'decks.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(decks_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Généré : {json_path}")

# --- GÉNÉRATION DU HTML ---
def generate_html(decks_data):
    """Génère une page HTML avec les liens de téléchargement"""
    
    # Calcul des statistiques
    total_decks = sum(len(decks) for decks in decks_data.values()) if decks_data else 0
    total_subjects = len(decks_data) if decks_data else 0
    
    html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Decks Anki PTSI - Téléchargements</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}
        
        .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 2rem;
        }}
        
        .subject-section {{
            margin-bottom: 2.5rem;
        }}
        
        .subject-title {{
            font-size: 1.5rem;
            color: #667eea;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #667eea;
            font-weight: 600;
        }}
        
        .deck-list {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        
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
            background: #e9ecef;
            border-color: #667eea;
            transform: translateX(5px);
        }}
        
        .deck-info {{
            flex: 1;
        }}
        
        .deck-name {{
            font-weight: 600;
            color: #2d3748;
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }}
        
        .deck-size {{
            font-size: 0.875rem;
            color: #718096;
        }}
        
        .download-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.6rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.2s ease;
            display: inline-block;
        }}
        
        .download-btn:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .empty-state {{
            text-align: center;
            padding: 3rem 2rem;
            color: #718096;
        }}
        
        .empty-state h2 {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #2d3748;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 2rem;
            text-align: center;
            color: #718096;
            border-top: 1px solid #e2e8f0;
        }}
        
        footer a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: 700;
            color: white;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        @media (max-width: 600px) {{
            h1 {{
                font-size: 1.8rem;
            }}
            
            .content {{
                padding: 1.5rem;
            }}
            
            .deck-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }}
            
            .download-btn {{
                width: 100%;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 Decks Anki PTSI</h1>
            <p class="subtitle">Téléchargez vos flashcards pour réviser efficacement</p>
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
        
        <div class="content">
"""
    
    # Si aucun deck, afficher un message
    if not decks_data or total_decks == 0:
        html_content += """
            <div class="empty-state">
                <h2>📦 Aucun deck disponible pour le moment</h2>
                <p>Les decks seront générés automatiquement lors du prochain push sur le repository.</p>
                <p style="margin-top: 1rem;">En attendant, vous pouvez consulter le <a href="https://github.com/CermP/anki-ptsi" style="color: #667eea; font-weight: 600;">code source sur GitHub</a>.</p>
            </div>
"""
    else:
        # Génération des sections par matière
        for subject in sorted(decks_data.keys()):
            decks = decks_data[subject]
            html_content += f"""
            <div class="subject-section">
                <h2 class="subject-title">{subject}</h2>
                <div class="deck-list">
"""
            
            for deck in decks:
                html_content += f"""
                    <div class="deck-item">
                        <div class="deck-info">
                            <div class="deck-name">{deck['name']}</div>
                            <div class="deck-size">{deck['size']}</div>
                        </div>
                        <a href="{deck['filename']}" class="download-btn" download>⬇️ Télécharger</a>
                    </div>
"""
            
            html_content += """
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <footer>
            <p>🚀 Généré automatiquement depuis le repo <a href="https://github.com/CermP/anki-ptsi" target="_blank">CermP/anki-ptsi</a></p>
            <p style="margin-top: 0.5rem;">🤝 Contributions bienvenues ! N'hésitez pas à participer au projet.</p>
        </footer>
    </div>
</body>
</html>
"""
    
    html_path = os.path.join(OUTPUT_DIR, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"✅ Généré : {html_path}")

# --- LANCEMENT ---
if __name__ == "__main__":
    print("🔨 Génération de l'index des decks...")
    print(f"📂 Dossier de sortie : {OUTPUT_DIR}")
    
    decks_data = collect_decks()
    
    # Générer les fichiers même s'il n'y a pas de decks
    generate_json(decks_data)
    generate_html(decks_data)
    
    if not decks_data:
        print("⚠️ Aucun deck trouvé dans le dossier output/")
        print("📝 Page HTML générée avec message d'attente")
    else:
        total = sum(len(d) for d in decks_data.values())
        print(f"✨ Index généré avec succès ! {total} decks disponibles dans {len(decks_data)} matières.")
