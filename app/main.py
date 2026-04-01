import streamlit as st
import sys
import os

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pdf_parser import process_pdf, validate_pdf_file, save_pdf_as_markdown
from core.web_parser import extract_text_from_url, is_valid_url, get_webpage_title
from core.summarizer import generate_summary_with_ollama, save_summary_to_file, get_installed_ollama_models
from core.complexity_analyzer import calculate_technical_score

st.set_page_config(
    page_title="Crypto Whitepaper Analyzer", 
    page_icon="📄", 
    layout="wide"
)

# Initialiser la session state
if 'document_text' not in st.session_state:
    st.session_state.document_text = None
if 'document_name' not in st.session_state:
    st.session_state.document_name = None
if 'document_type' not in st.session_state:
    st.session_state.document_type = None  # 'pdf' ou 'web'

# Header
st.title("📄 Crypto Whitepaper Analyzer")

# Menu de navigation
st.sidebar.header("🧭 Navigation")
page = st.sidebar.radio(
    "Choisissez une section :",
    ["🏠 Accueil", "📊 Analyse", "🤖 Résumé", "🔍 Recherche"]
)

# Afficher le document courant
if st.session_state.document_text:
    st.sidebar.success(f"📄 Document chargé : {st.session_state.document_name}")
else:
    st.sidebar.warning("📤 Aucun document chargé")

st.markdown("---")

# Page Accueil
if page == "🏠 Accueil":
    st.write("### Bienvenue !")
    st.write("Analysez les whitepapers de projets cryptomonnaies avec l'IA.")
    st.write("")
    
    # Tabs pour différentes sources
    tab1, tab2 = st.tabs(["📤 PDF Upload", "🌐 Lien Web"])
    
    # Tab 1 : Upload PDF
    with tab1:
        st.header("📄 Upload de PDF")
        uploaded_file = st.file_uploader(
            "Choisissez un fichier PDF", 
            type="pdf",
            key="pdf_uploader"
        )
        
        if uploaded_file is not None:
            # Validation du PDF
            is_valid, validation_message = validate_pdf_file(uploaded_file)
            
            if not is_valid:
                st.error(f"❌ Fichier invalide : {validation_message}")
            else:
                try:
                    with st.spinner("_extraction du texte en cours..."):
                        uploaded_file.seek(0)
                        text, page_count = process_pdf(uploaded_file)
                        
                    if text and len(text.strip()) > 0:
                        st.success("✅ Document PDF valide et traité avec succès !")
                    
                        try:
                            uploaded_file.seek(0)
                            md_filepath = save_pdf_as_markdown(uploaded_file, text)
                            st.success(f"💾 PDF également sauvegardé en Markdown : {md_filepath}")
                        except Exception as save_error:
                            st.warning(f"⚠️ Sauvegarde Markdown échouée : {save_error}")
                        
                        # Stocker dans session state
                        st.session_state.document_text = text
                        st.session_state.document_name = uploaded_file.name
                        st.session_state.document_type = 'pdf'
                        
                        # Afficher un aperçu
                        with st.expander("🔍 Aperçu du contenu extrait", expanded=False):
                            preview_text = text[:1500] + "..." if len(text) > 1500 else text
                            st.text_area("Aperçu du contenu", value=preview_text, height=200, key="preview", label_visibility="collapsed")
                        
                        # Statistiques
                        char_count = len(text)
                        word_count = len(text.split())
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("🔤 Caractères", f"{char_count:,}")
                        col2.metric("📝 Mots", f"{word_count:,}")
                        col3.metric("📄 Pages", page_count)
                        
                        st.info("✅ Votre document est prêt ! Utilisez le menu de navigation à gauche.")
                        
                    else:
                        st.warning("⚠️ Le PDF ne contient pas de texte lisible")
                        
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {str(e)}")
    
    # Tab 2 : Lien Web
    with tab2:
        st.header("🌐 Analyse de page web")
        st.write("Entrez l'URL d'un whitepaper en ligne (GitBook, documentation, etc.)")
        
        url = st.text_input("URL du document :", 
                           placeholder="https://example.gitbook.io/whitepaper",
                           key="url_input")
        
        if url:
            if not is_valid_url(url):
                st.error("❌ URL invalide. Veuillez entrer une URL complète commençant par http:// ou https://")
            else:
                if st.button("📥 Extraire le contenu"):
                    try:
                        with st.spinner("_extraction du contenu web en cours..."):
                            text = extract_text_from_url(url)
                            title = get_webpage_title(url)
                        
                        if text and len(text.strip()) > 50:
                            st.success("✅ Contenu web extrait avec succès !")
                            
                            # Stocker dans session state
                            st.session_state.document_text = text
                            st.session_state.document_name = title
                            st.session_state.document_type = 'web'
                            
                            # Afficher un aperçu
                            with st.expander("🔍 Aperçu du contenu extrait", expanded=False):
                                preview_text = text[:1500] + "..." if len(text) > 1500 else text
                                st.text_area("Aperçu de contenu", value=preview_text, height=200, key="web_preview", label_visibility="collapsed")
                            
                            # Statistiques
                            char_count = len(text)
                            word_count = len(text.split())
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("🔤 Caractères", f"{char_count:,}")
                            col2.metric("📝 Mots", f"{word_count:,}")
                            col3.metric("📄 Type", "Web")
                            
                            st.info("✅ Votre document web est prêt ! Utilisez le menu de navigation à gauche.")
                            
                        else:
                            st.warning("⚠️ Aucun contenu texte trouvé sur cette page")
                            
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'extraction : {str(e)}")
                        st.info("💡 Vérifiez que l'URL est accessible et que le site autorise le scraping")

# Pages à venir...
elif page == "📊 Analyse":
    if st.session_state.document_text:
        st.header("📊 Analyse du document")
        
        # === Analyse de Complexité/Technicité ===
        st.subheader("🔬 Score de Technicité")
        
        with st.spinner("Calcul du score de technicité..."):
            try:
                complexity_result = calculate_technical_score(st.session_state.document_text)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("📈 Score Normalisé", f"{complexity_result['score_normalise']:.2f}%")
                col2.metric("🔢 Score Brut", f"{complexity_result['score_brut']:,}")
                col3.metric("📝 Mots Analysés", f"{complexity_result['total_mots']:,}")
                
                # Afficher les termes les plus fréquents
                # Vérifier que 'termes_trouves' est bien un dictionnaire
                termes_trouves_data = complexity_result.get('termes_trouves', {})

                if isinstance(termes_trouves_data, dict) and termes_trouves_data:
                    st.write("**Termes techniques identifiés :**")
                    # Trier par fréquence
                    try:
                        sorted_terms = sorted(termes_trouves_data.items(), key=lambda item: item[1], reverse=True)
                        # Afficher les 15 premiers
                        for term, count in sorted_terms[:15]:
                            st.markdown(f"`{term}` ({count}x)")
                    except Exception as sort_error:
                        st.warning(f"⚠️ Impossible de trier les termes trouvés : {sort_error}")
                        # Affichage simple sans tri si le tri échoue
                        for term, count in list(termes_trouves_data.items())[:15]:
                             st.markdown(f"`{term}` ({count}x)")
                elif isinstance(termes_trouves_data, dict):
                    st.info("Aucun terme technique du dictionnaire n'a été trouvé.")
                else:
                    # Cas où termes_trouves_data n'est pas un dict (float, int, etc.)
                    st.error(f"Erreur inattendue : 'termes_trouves' n'est pas un dictionnaire. Type reçu : {type(termes_trouves_data)}")
                    
            except Exception as e:
                st.error(f"Erreur lors de l'analyse de complexité : {e}")
        # ========================================
        
        # Placeholder pour d'autres analyses
        st.write("---")
        st.write("D'autres analyses seront disponibles prochainement :")
        st.write("- 📊 Analyse statistique avancée")
        st.write("- 🔤 Extraction de mots-clés")
        st.write("- 🏷️ Reconnaissance d'entités")
        
    else:
        st.warning("📤 Veuillez d'abord charger un document (PDF ou URL).")

elif page == "🤖 Résumé":
    if st.session_state.document_text:
        st.header("🤖 Résumé et Analyse Structurée")
        
        st.write("Voici une analyse structurée du document :")
        
        # === Récupération dynamique des modèles ===
        with st.spinner("🔍 Récupération des modèles Ollama disponibles..."):
            # Appel de la fonction pour obtenir la liste
            available_models = get_installed_ollama_models()
        
        # Gestion des cas d'erreur / absence de modèles
        if not available_models:
            # Afficher un message d'erreur clair
            st.error("❌ Impossible de récupérer la liste des modèles Ollama.")
            st.info("💡 **Conseils :**\n"
                    "1. Assurez-vous qu'Ollama est **installé** sur votre machine.\n"
                    "2. Assurez-vous qu'Ollama est **en cours d'exécution**. Ouvrez un terminal et tapez `ollama serve`.\n"
                    "3. Vérifiez si vous avez **téléchargé au moins un modèle**. Par exemple, dans un terminal : `ollama pull qwen3:8b`."
            )
            # Arrêter l'exécution de cette section de la page
            st.stop() 
        
        # Si des modèles sont trouvés, on continue
        # Définir un modèle par défaut s'il est disponible
        default_model = "qwen3:8b"
        default_index = available_models.index(default_model) if default_model in available_models else 0

        # Sélection du modèle parmi ceux disponibles
        model_choice = st.selectbox(
            'Choisissez un modèle LLM installé :',
            available_models,
            index=default_index,
            key="model_selector"
        )
        if not model_choice:
     # Cela ne devrait normalement pas arriver, mais on prévient une erreur de type
            model_choice = available_models[0] if available_models else "qwen3:8b" # Valeur par défaut absolue


        # Option de sauvegarde
        save_option = st.checkbox("💾 Sauvegarder le résumé généré", value=True)
        
        if st.button("🚀 Générer l'analyse"):
            with st.spinner("🧠 Analyse en cours avec Ollama..."):
                try:                    
                    # Utiliser un nom par défaut si document_name est None ou vide
                    doc_name_to_use = st.session_state.document_name or "document_sans_nom"
                    
                    # Appeler la fonction avec le texte du document
                    # model_choice est défini plus haut et accessible ici
                    summary = generate_summary_with_ollama(
                        st.session_state.document_text, 
                        model= model_choice,
                        document_name=doc_name_to_use
                    )
                    
                    st.subheader("📋 Plan Structuré")
                    st.markdown(summary)
                    
                    # Sauvegarder si demandé
                    if save_option:
                        if summary and len(summary.strip()) > 50 and not summary.startswith(("❌", "⚠️")):
                            try:
                                filepath = save_summary_to_file(
                                    summary, 
                                    doc_name_to_use, 
                                    model_choice  # Utilisation de model_choice
                                )
                                st.success(f"💾 Résumé sauvegardé dans : {filepath}")
                            except Exception as save_error:
                                st.error(f"❌ Sauvegarde échouée : {save_error}")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération : {e}")
    else:
        st.warning("📤 Veuillez d'abord charger un document (PDF ou URL).")
        
elif page == "🔍 Recherche":
    st.header("🔍 Recherche dans les documents")
    st.info("Cette fonctionnalité sera disponible prochainement")

# Footer
st.markdown("---")
st.caption("📄 Crypto Whitepaper Analyzer - 2025")