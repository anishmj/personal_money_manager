from pathlib import Path

import streamlit as st


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STYLESHEET_PATHS = (
    STATIC_DIR / "bootstrap.min.css",
    STATIC_DIR / "app.css",
)


def _load_stylesheet() -> str:
    stylesheets = []
    for path in STYLESHEET_PATHS:
        if not path.is_file():
            raise FileNotFoundError(f"Required stylesheet is missing: {path}")
        stylesheets.append(path.read_text(encoding="utf-8"))
    return "\n".join(stylesheets)


def inject_app_styles() -> None:
    bootstrap_css = BOOTSTRAP_STYLESHEET_PATH.read_text(encoding="utf-8")
    app_css = _load_stylesheet()
    st.markdown(
        f"<style>{bootstrap_css}\n{app_css}</style>",
        unsafe_allow_html=True
    )
