
import json
import urllib.request
import unicodedata
import re
import os
from typing import Any, Dict, Optional

ANKI_CONNECT_URL: str = "http://localhost:8765"

def anki_connect_request(action: str, **params: Any) -> Optional[Dict[str, Any]]:
    """
    Communiquer avec Anki via l'add-on AnkiConnect.
    """
    try:
        request_data = json.dumps({
            "action": action,
            "params": params,
            "version": 6
        }).encode("utf-8")
        
        request = urllib.request.Request(ANKI_CONNECT_URL, request_data)
        
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
            
        if len(result) != 2:
            raise Exception("Réponse inattendue d'AnkiConnect")
            
        if result.get("error") is not None:
            raise Exception(result["error"])
            
        return result
        
    except Exception as e:
        print(f"\n[ERREUR] Impossible de connecter à Anki : {e}")
        print("Vérifiez qu'Anki est ouvert et que l'add-on AnkiConnect est installé.")
        return None

def slugify(value: str) -> str:
    """
    Normalise une chaîne de caractères pour l'utiliser dans les noms de fichiers ou d'ID.
    Supprime les accents et remplace les caractères spéciaux.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '_', value)
