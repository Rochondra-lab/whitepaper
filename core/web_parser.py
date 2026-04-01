import requests
import re
import os
from bs4 import BeautifulSoup
from gitbook_scraper import GitbookScraper
 

def extract_text_from_url(url: str) -> str:
    """
    Extrait le texte d'une page web (GitBook, documentation, etc.) avec gitbook-scraper
    """
    try:
        print("🔄 Utilisation de GitBook Scraper...")
        
        title = get_webpage_title(url)
        safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title) or "document"
        
        # Définir le dossier de sortie
        output_dir = r"data\whitepaper\gitbooks"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{safe_title}.md")
        
        scraper = GitbookScraper( 
            base_url=url.strip(),
            output_file=output_file,
            generate_toc=True,
            delay=0.5
        )
        scraper.scrape() # Génère le fichier
        
        # Lire le fichier généré
        # Vérifier si le fichier existe à l'endroit où le scraper l'a réellement créé
        print(f"🔍 Recherche du fichier généré : {output_file}")
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                content = re.sub(r'\n{3,}', '\n\n', content)
                return content.strip()
        else:
             raise Exception(f"Fichier non généré par GitBook Scraper à l'emplacement attendu '{output_file}'. Vérifiez le nom et l'emplacement.")
            
    except Exception as e:
        raise Exception(f"Erreur lors de l'extraction avec GitBook Scraper : {str(e)}")

def is_valid_url(url: str) -> bool:
    """Vérifie si une chaîne est une URL valide"""
    url_pattern = re.compile(
        r'^https?://'  # http:// ou https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domaine
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url.strip()) is not None # Nettoyer l'URL

def get_webpage_title(url: str) -> str:
    """Récupère le titre d'une page web"""
    try:
        url = url.strip()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('title')
        
        if title:
            clean_title = title.text.strip()
            clean_title = re.sub(r'\s+', ' ', clean_title)
            return clean_title
        else:
            return "Document web"
        
    except Exception as e:
        print(f"⚠️ Impossible de récupérer le titre : {e}")
        return "Document web"


if __name__ == "__main__":

    test_url = "https://whitepaper.aicogni.io/"
    
    print("🔍 Test d'extraction avec :", test_url)
    print("=" * 50)
    
    try:

        text = extract_text_from_url(test_url)
        title = get_webpage_title(test_url)
        
        print(f"✅ Contenu extrait avec succès !")
        print(f"📏 Caractères extraits : {len(text)}")
        print(f"📝 Mots extraits : {len(text.split())}")
        print("\n📄 Aperçu du contenu (500 premiers caractères) :")
        print("-" * 50)
        print(text[:500] + "..." if len(text) > 500 else text)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
