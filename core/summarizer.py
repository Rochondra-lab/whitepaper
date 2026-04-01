import requests
import json
import re
import os
from datetime import datetime

def get_installed_ollama_models(host="http://localhost:11434"):
    """
    Récupère la liste des modèles installés via l'API Ollama.
    
    Args:
        host (str): L'URL de base du serveur Ollama (par défaut localhost:11434).
        
    Returns:
        list: Une liste de noms de modèles (str), ou une liste vide en cas d'erreur.
    """
    data= None # Initialisation au début du try block pour éviter UnboundLocalError
    try:
        url = f"{host}/api/tags"
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Lève une exception pour les codes d'erreur 4xx/5xx
        
        data = response.json()
        # La réponse contient une clé 'models' qui est une liste de dictionnaires
        # Chaque dictionnaire a une clé 'name'
        model_names = [model['name'] for model in data.get('models', [])]
        return model_names
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à Ollama à l'adresse {host}. Assurez-vous qu'il est en cours d'exécution.")
        return []
    except requests.exceptions.Timeout:
        print(f"❌ Timeout lors de la requête à Ollama ({host}).")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la requête à Ollama : {e}")
        return []
    except KeyError:
        # Si la structure de la réponse n'est pas celle attendue
        print(f"⚠️ Réponse inattendue de l'API Ollama : {data}")
        return []
    except Exception as e:
        print(f"❌ Une erreur inattendue s'est produite : {e}")
        return []

def generate_summary_with_ollama(text: str, model: str = "qwen3:8b", document_name: str = "document") -> str:
    """
    Génère un résumé ou un plan structuré d'un texte en utilisant un modèle Ollama.
    Enregistre également la réponse brute du modèle au format JSON.
    """
    # 🔍 Nettoyage basique du texte
    cleaned_text = re.sub(r'\s+', ' ', text).strip()
    print(f"📄 Longueur du texte nettoyé : {len(cleaned_text)} caractères.")


    # 1. Définir le prompt
    prompt = [
        {
            "role": "system",
            "content": (
                "You are an assistant specialized in analyzing technical documents and blockchain. "
                "Your task is to analyze the text of a blockchain project's whitepaper"
                "and extract a detailed and structured outline."
            )
        },
        {
            "role": "user",
            "content": f"""FOLLOW THESE INSTRUCTIONS EXACTLY:

    1. IDENTIFY the main sections of the document based on its table of contents or logical structure.
    2. FOR EACH identified section, provide:
    - Its number (e.g., 1, 2, 3…)
    - Its exact title
    - A concise summary (2–3 sentences) of the main content of the section.
    - If a mathematical formula is present, include it exactly as it appears. If no formula is present, omit the line.

    3. STRICTLY FOLLOW the output format below, with no additional text:
    1. SECTION TITLE 1
    Summary: ...
    Formula: ... (only if present)
    2. SECTION TITLE 2
    Summary: ...
    Formula: ... (only if present)
    ...

    4. DO NOT ADD ANY OTHER INFORMATION.

    Here is the content of the document:
    {cleaned_text}"""
        }
    ]



    # 2. Préparer la requête pour l'API Ollama
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.5,
        }
    }

    print(f"\n--- Envoi de la requête à {model} via Ollama ---")
    
    try:
        # === NOUVEAU : Enregistrer la requête ===
        _save_raw_data(payload, document_name, model, "request")
        
        # 3. Envoyer la requête POST
        response = requests.post(url, json=payload, timeout=120)

        # 4. Vérifier la réponse
        if response.status_code == 200:
            # === NOUVEAU : Enregistrer la réponse brute ===
            raw_data = response.json()
            _save_raw_data(raw_data, document_name, model, "response")
            
            raw_response = raw_data.get("response", "")
            
            # === Traitement existant (simplifié pour le debug) ===
            # Retirer la balise <think> si présente (version simplifiée)
            if "<think>" in raw_response and "</think>" in raw_response:
                # Trouver la fin de </think>
                end_think_index = raw_response.find("</think>") + len("</think>")
                # Prendre tout ce qui suit
                processed_response = raw_response[end_think_index:].strip()
                print("🧹 Balise <think> détectée et retirée.")
            else:
                processed_response = raw_response.strip()
            
            if processed_response:
                print("\n--- Plan généré avec succès (après nettoyage basique) ---")
                print(f"📏 Longueur du résumé final : {len(processed_response)} caractères")
                # On affiche un petit aperçu pour vérifier
                lines_preview = processed_response.split('\n')[:5]
                print("👀 Aperçu des premières lignes :")
                for line in lines_preview:
                    print(f"   {line}")
                return processed_response
            else:
                error_msg = "⚠️ Réponse vide reçue du modèle après nettoyage."
                print(error_msg)
                return error_msg
        else:
            error_msg = f"❌ Erreur Ollama ({response.status_code}): {response.text}"
            print(error_msg)
            return error_msg

    except requests.exceptions.ConnectionError:
        error_msg = "❌ Erreur de connexion. Assure-toi qu'Ollama est en cours d'exécution (`ollama serve`)."
        print(error_msg)
        return error_msg
    except requests.exceptions.Timeout:
        error_msg = "❌ Timeout lors de la requête à Ollama. Le modèle met trop de temps à répondre."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Une erreur s'est produite : {e}"
        print(error_msg)
        return error_msg

def _save_raw_data(data: dict, document_name: str, model: str, data_type: str):
    """
    Enregistre les données brutes (requête ou réponse) au format JSON.
    
    Args:
        data (dict): Les données à sauvegarder.
        document_name (str): Nom du document source.
        model (str): Nom du modèle utilisé.
        data_type (str): Type de données ("request" ou "response").
    """
    try:
        # Créer le dossier pour les données brutes
        save_dir = "data/whitepaperLLM_Raw"
        os.makedirs(save_dir, exist_ok=True)
        
        # Créer un nom de fichier sécurisé
        safe_doc_name = re.sub(r'[^\w\s-]', '', document_name)[:30].strip()
        safe_doc_name = re.sub(r'[-\s]+', '-', safe_doc_name) or "document"
        
        # Nettoyer le nom du modèle
        safe_model_name = re.sub(r'[^\w]', '_', model)
        
        # Ajouter timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_doc_name}_{safe_model_name}_{data_type}_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)
        
        # Ajouter des métadonnées
        data_to_save = {
            "metadata": {
                "document_name": document_name,
                "model": model,
                "type": data_type,
                "timestamp": timestamp,
                "source_file": filepath
            },
            "data": data
        }
        
        # Écrire dans le fichier
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Données brutes ({data_type}) sauvegardées dans : {filepath}")
        
    except Exception as e:
        print(f"⚠️ Erreur lors de la sauvegarde des données brutes ({data_type}) : {e}")

# (Le reste des fonctions comme save_summary_to_file reste inchangé)
# ... [Le code existant de save_summary_to_file suit] ...S

def save_summary_to_file(summary: str, document_name: str, model: str, save_dir: str = "data/whitepaperLLM_Output") -> str:
    """
    Enregistre le résumé généré dans un fichier
    """
    try:
        print(f"\n💾 Tentative de sauvegarde du résumé...")
        print(f"   Longueur du summary reçu : {len(summary)}")
        print(f"   Document name : {document_name}")
        print(f"   Model : {model}")
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(save_dir, exist_ok=True)
        print(f"   Dossier {save_dir} prêt.")
        
        # Créer un nom de fichier sécurisé et compatible
        safe_doc_name = re.sub(r'[^\w\s-]', '', document_name)[:50].strip()
        safe_doc_name = re.sub(r'[-\s]+', '-', safe_doc_name) or "document"
        
        # Nettoyer aussi le nom du modèle pour éviter les caractères problématiques (:)
        safe_model_name = re.sub(r'[^\w\s-]', '_', model) # Remplacer : par _
        
        # Ajouter timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_doc_name}_{safe_model_name}_{timestamp}.md"
        filepath = os.path.join(save_dir, filename)
        
        print(f"   Chemin du fichier : {filepath}")
        
        # Créer le contenu du fichier
        content = f"""# Résumé généré par LLM
Document source: {document_name}
Modèle utilisé: {model}
Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Longueur du résumé: {len(summary)} caractères

---

{summary}
"""
        print(f"   Longueur du contenu à écrire : {len(content)}")
        
        # Écrire dans le fichier
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Résumé sauvegardé dans : {filepath}")
        return filepath
        
    except Exception as e:
        error_msg = f"❌ Erreur lors de la sauvegarde du résumé : {str(e)}"
        print(error_msg)
        # Même en cas d'erreur, on tente de créer un fichier d'erreur
        try:
            error_filename = f"ERROR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            error_filepath = os.path.join(save_dir, error_filename)
            with open(error_filepath, 'w', encoding='utf-8') as ef:
                 ef.write(f"Erreur de sauvegarde : {str(e)}\n")
                 ef.write(f"Contenu summary (1000 premiers caractères) : {summary[:1000]}\n")
            print(f"📝 Fichier d'erreur écrit : {error_filepath}")
        except:
            pass
        raise Exception(error_msg)

# Pour les tests
if __name__ == "__main__":
    models = get_installed_ollama_models()
    if models:
        print("✅ Modèles Ollama installés :")
        for model in models:
            print(f"  - {model}")
    else:
        print("⚠️ Aucun modèle trouvé ou erreur de connexion.")    
    # Test simple
    test_summary = "1. Introduction\nRésumé: Ceci est un test.\n2. Conclusion\nRésumé: Fin du test."
    save_summary_to_file(test_summary, "test_doc", "test_model")