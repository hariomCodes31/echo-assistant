import os
import json
import streamlit as st

class ThemeEngine:
    THEMES_DIR = "themes"

    @classmethod
    def get_available_themes(cls):
        """Scans the themes/ directory and loads metadata from theme.json files."""
        themes = []
        if not os.path.exists(cls.THEMES_DIR):
            os.makedirs(cls.THEMES_DIR)
        
        for d in sorted(os.listdir(cls.THEMES_DIR)):
            path = os.path.join(cls.THEMES_DIR, d)
            if os.path.isdir(path):
                meta_path = os.path.join(path, "theme.json")
                if os.path.exists(meta_path):
                    try:
                        with open(meta_path, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            meta["id"] = d
                            themes.append(meta)
                    except Exception:
                        pass
        return themes

    @classmethod
    def get_theme(cls, theme_id):
        """Returns metadata for a specific theme, falling back to Quantum HUD."""
        themes = cls.get_available_themes()
        for t in themes:
            if t["id"] == theme_id:
                return t
        
        # Fallback to Quantum
        return {
            "id": "quantum",
            "name": "Quantum HUD",
            "description": "Deep blue holographic interface with animated system core reactor",
            "accent_color": "#00D9FF",
            "accent_glow": "rgba(0, 217, 255, 0.35)",
            "primary_font": "Orbitron",
            "preview_emoji": "💠"
        }

    @classmethod
    def get_theme_css(cls, theme_id):
        """Reads and returns the custom CSS file for the theme."""
        css_path = os.path.join(cls.THEMES_DIR, theme_id, "theme.css")
        if os.path.exists(css_path):
            try:
                with open(css_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return ""

    @classmethod
    def get_theme_js(cls, theme_id):
        """Reads and returns the custom JavaScript file for the theme."""
        js_path = os.path.join(cls.THEMES_DIR, theme_id, "theme.js")
        if os.path.exists(js_path):
            try:
                with open(js_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return ""

    @classmethod
    def get_theme_core_html(cls, theme_id):
        """Reads and returns the AI core HTML content for the theme."""
        html_path = os.path.join(cls.THEMES_DIR, theme_id, "core.html")
        if os.path.exists(html_path):
            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return None

    @classmethod
    def get_theme_stats_html(cls, theme_id):
        """Reads and returns the custom stats widget HTML content for the theme."""
        html_path = os.path.join(cls.THEMES_DIR, theme_id, "stats.html")
        if os.path.exists(html_path):
            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return None

    @classmethod
    def get_theme_background_html(cls, theme_id):
        """Reads and returns the custom background HTML content for the theme."""
        html_path = os.path.join(cls.THEMES_DIR, theme_id, "background.html")
        if os.path.exists(html_path):
            try:
                with open(html_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass
        return None

