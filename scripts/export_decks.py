import json
import urllib.request
import csv
import os
import html

# --- CONFIGURATION ---
OUTPUT_DIR = "../decks"  # Dossier de sortie (relatif au script)
ANKI_URL = "http://localhost:8765"

# --- FONCTION DE COMMUNICATION AVEC ANKI ---
def request(action, **params):
    try:
        response = json.load(urllib.request.urlopen(urllib.request.Request(ANKI_URL, json.dumps({
            "action": action,
            "params": params,
            "version": 6
        }).encode("utf-8"))))
        if len(response) != 2:
            raise Exception("Réponse inattendue d'AnkiConnect")
        if response.get("error") is not None:
            raise Exception(response["error"])
        return response
    except Exception as e:
        print(f"\n[ERREUR] Impossible de connecter à Anki : {e}")
        print("Vérifiez qu'Anki est ouvert et que l'add-on AnkiConnect est installé.")
        return None

# --- FONCTION PRINCIPALE ---
def main():
    # 1. Récupérer la liste des decks
    response = request("deckNames")
    if not response: return # On arrête si erreur
    
    all_decks = response["result"]
    
    # 2. Affichage du Menu de Sélection
    print("\n--- DECKS DISPONIBLES DANS ANKI ---")
    for index, name in enumerate(all_decks):
        print(f"[{index}] {name}")
    
    print("\n-----------------------------------")
    user_input = input("Entrez les numéros à exporter (séparés par une virgule, ou 'all' pour tout) : ")

    # 3. Traitement du choix utilisateur
    target_decks = []
    
    if user_input.lower().strip() == 'all' or user_input.strip() == '':
        target_decks = all_decks
        print("-> Sélection : TOUT exporter.")
    else:
        try:
            # On découpe la chaine "1, 3" en liste d'entiers [1, 3]
            indices = [int(x.strip()) for x in user_input.split(",")]
            
            # On récupère les noms correspondants aux numéros
            for i in indices:
                if 0 <= i < len(all_decks):
                    target_decks.append(all_decks[i])
                else:
                    print(f"[ATTENTION] Le numéro {i} n'existe pas, ignoré.")
        except ValueError:
            print("[ERREUR] Saisie invalide. Utilisez des nombres séparés par des virgules.")
            return

    if not target_decks:
        print("Aucun deck sélectionné. Fin du programme.")
        return

    # 4. Lancement de l'export (Boucle principale)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"\nDébut de l'export pour {len(target_decks)} deck(s)...")

    for deck in target_decks:
        print(f"📦 Export de '{deck}'...", end=" ")
        
        # Récupération des IDs des cartes
        find_notes = request("findNotes", query=f'"deck:{deck}"')
        notes_info = request("notesInfo", notes=find_notes["result"])
        
        # Nettoyage du nom de fichier (on évite les espaces et caractères bizarres)
        safe_name = deck.replace("::", "-").replace(" ", "_").replace("/", "-")
        filename = os.path.join(OUTPUT_DIR, f"{safe_name}.csv")
        
        try:
            # encoding="utf-8-sig" permet à Excel d'afficher correctement les accents
            with open(filename, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=";") # Séparateur point-virgule
                
                count = 0
                for note in notes_info["result"]:
                    fields_values = []
                    
                    # Nettoyage de chaque champ (décodage des entités HTML &#x27; etc.)
                    for f_obj in note["fields"].values():
                        raw_value = f_obj["value"]
                        clean_value = html.unescape(raw_value)
                        fields_values.append(clean_value)
                    
                    # Ajout des tags en dernière colonne
                    tags = " ".join(note["tags"])
                    fields_values.append(tags) 
                    
                    writer.writerow(fields_values)
                    count += 1
            print(f"✅ OK ({count} cartes)")
            
        except Exception as e:
            print(f"❌ ERREUR : {e}")

    print("\n--- Terminé ! Pensez à faire votre git push ---")

if __name__ == "__main__":
    main()
