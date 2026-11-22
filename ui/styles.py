from pathlib import Path

import streamlit as st


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
STYLESHEET_PATH = STATIC_DIR / "dashboard.css"


@st.cache_data(show_spinner=False)
def _load_stylesheet() -> str:
    if not STYLESHEET_PATH.is_file():
        raise FileNotFoundError(f"Required stylesheet is missing: {STYLESHEET_PATH}")
    return STYLESHEET_PATH.read_text(encoding="utf-8")


def inject_app_styles() -> None:
    st.markdown(
        f"<style>{_load_stylesheet()}</style>",
        unsafe_allow_html=True
    )
