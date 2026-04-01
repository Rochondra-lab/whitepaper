import PyPDF2
import os
import re
from typing import Union, BinaryIO, Tuple
from datetime import datetime

def process_pdf(pdf_file: Union[str, BinaryIO]) -> Tuple[str, int]:
    """
    Extrait le texte et compte le nombre de pages d'un fichier PDF.
    
    Args:
        pdf_file: Chemin du fichier (str) ou objet fichier binaire.
        
    Returns:
        Tuple[str, int]: Un tuple contenant (texte_extrait, nombre_de_pages).
        
    Raises:
        Exception: Si une erreur se produit lors du traitement du PDF.
    """
    try:

        pdf_reader = PyPDF2.PdfReader(pdf_file)
            
        # Compter les pages
        page_count = len(pdf_reader.pages)
        
        # Extraire le texte
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip(), page_count
        
    except Exception as e:
        # Fournir un message d'erreur plus informatif
        raise Exception(f"Erreur lors du traitement du PDF : {str(e)}")

def validate_pdf_file(uploaded_file) -> tuple[bool, str]:
    """Validation complète d'un fichier PDF"""
    try:
        if hasattr(uploaded_file, 'name'):
            if not uploaded_file.name.lower().endswith('.pdf'):
                return False, "Le fichier doit être au format PDF (.pdf)"
        
        if hasattr(uploaded_file, 'read'):
            uploaded_file.seek(0)
            header = uploaded_file.read(4)
            uploaded_file.seek(0)
            if header != b'%PDF':
                return False, "Le fichier n'est pas un PDF valide (header incorrect)"
        
        if hasattr(uploaded_file, 'read'):
            uploaded_file.seek(0)
            reader = PyPDF2.PdfReader(uploaded_file)
            len(reader.pages)
        return True, "PDF valide"
    
    except Exception as e:
        return False, f"PDF corrompu ou protégé : {str(e)}"

def save_pdf_as_markdown(pdf_file, text: str, filename: str = "", save_dir: str = "data/whitepaper/pdf") -> str:
    """
    Enregistre le texte extrait d'un PDF au format Markdown (texte brut seulement)
    
    Args:
        pdf_file: Fichier PDF (objet ou chemin) - utilisé uniquement pour le nom
        text: Texte extrait du PDF
        filename: Nom du fichier (optionnel)
        save_dir: Dossier de sauvegarde
    
    Returns:
        Chemin du fichier Markdown créé
    """
    try:
        # Créer le dossier s'il n'existe pas
        os.makedirs(save_dir, exist_ok=True)
        
        # Créer un nom de fichier
        if filename:
            # Utiliser le nom fourni
            safe_filename = re.sub(r'[^\w\s-]', '', filename)[:50].strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            if not safe_filename:
                safe_filename = "document"
        else:
            # Utiliser le nom du fichier PDF ou générer un nom
            if hasattr(pdf_file, 'name'):
                base_name = os.path.splitext(pdf_file.name)[0]
                safe_filename = re.sub(r'[^\w\s-]', '', base_name)[:50].strip()
                safe_filename = re.sub(r'[-\s]+', '-', safe_filename) or "pdf_document"
            else:
                safe_filename = "pdf_document"
        
        # Ajouter timestamp et extension
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        md_filename = f"{safe_filename}_{timestamp}.md"
        filepath = os.path.join(save_dir, md_filename)
        
        # Écrire seulement le texte dans le fichier (format Markdown simple)
        # On peut ajouter un titre basé sur le nom du fichier
        md_content = f"# {safe_filename.replace('-', ' ').title()}\n\n{text}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filepath
        
    except Exception as e:
        raise Exception(f"Erreur lors de la sauvegarde en Markdown : {str(e)}")

# Pour les tests
if __name__ == "__main__":
    print("Module pdf_parser prêt avec sauvegarde Markdown")