import streamlit as st
import locale

# Langue par défaut
DEFAULT_LANG = "fr"

# Liste des langues supportées
SUPPORTED_LANGUAGES = [
    "fr", "en", "es", "sw", "ha", "yo", "ig", "zh", "hi", "rw",
    "ln", "sn", "tn", "st", "mg", "am", "om", "wo", "bm", "ts"
]

def get_user_language():
    """Détecte la langue préférée de l'utilisateur depuis session_state ou système"""
    # Vérifie si la langue est déjà en session
    if "selected_lang" in st.session_state:
        return st.session_state["selected_lang"]

    # Tente de détecter depuis le système
    try:
        sys_lang = locale.getdefaultlocale()[0][:2].lower()
        if sys_lang in SUPPORTED_LANGUAGES:
            return sys_lang
    except:
        pass

    # Fallback
    return DEFAULT_LANG

def set_user_language(lang):
    """Définit la langue choisie par l'utilisateur dans session_state"""
    if lang in SUPPORTED_LANGUAGES:
        st.session_state["selected_lang"] = lang
    else:
        st.session_state["selected_lang"] = DEFAULT_LANG

def language_selectbox():
    """Ajoute un selectbox dans la sidebar pour changer de langue"""
    lang_map = {
        "fr": "🇫🇷 Français", "en": "🇬🇧 English", "es": "🇪🇸 Español",
        "sw": "🌍 Swahili", "ha": "🇳🇬 Hausa", "yo": "🇳🇬 Yoruba", "ig": "🇳🇬 Igbo",
        "zh": "🇨🇳 中文", "hi": "🇮🇳 हिंदी", "rw": "🇷🇼 Kinyarwanda", "ln": "🇨🇩 Lingala",
        "sn": "🇿🇼 Shona", "tn": "🇧🇼 Tswana", "st": "🇱🇸 Sesotho", "mg": "🇲🇬 Malagasy",
        "am": "🇪🇹 Amharic", "om": "🇪🇹 Oromo", "wo": "🇸🇳 Wolof", "bm": "🇲🇱 Bambara", "ts": "🇿🇦 Tsonga"
    }

    selected = st.sidebar.selectbox(
        "🌐 Choisir la langue",
        options=list(lang_map.keys()),
        format_func=lambda x: lang_map[x],
        index=list(lang_map.keys()).index(get_user_language())
    )

    set_user_language(selected)
    return selected
