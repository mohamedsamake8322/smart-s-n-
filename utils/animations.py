import time
import streamlit as st

def typewriting_effect(placeholder, text, delay=0.04):
    """
    Affiche le texte progressivement avec un effet machine à écrire.
    Le paramètre `text` peut contenir du HTML (h1, p, etc.).
    """
    for i in range(len(text)):
        placeholder.markdown(text[:i+1], unsafe_allow_html=True)
        time.sleep(delay)

def pulsing_title(components):
    """
    Applique un effet de pulsation au titre <h1> (classe .animated-title si utilisée).
    Tu peux cibler tous les <h1>, ou uniquement ceux avec une classe CSS.
    """
    css_code = """
    <style>
    @keyframes pulse {
        0%   { transform: scale(1); }
        50%  { transform: scale(1.03); }
        100% { transform: scale(1); }
    }

    h1 {
        animation: pulse 2s infinite;
        transform-origin: center;
    }
    </style>
    """
    components.html(css_code, height=0)
