import streamlit as st
import pathlib


def load_css():
    """Load custom CSS styling"""
    script_dir = pathlib.Path(__file__).parent.parent  # Go up to app root
    css_path = script_dir / "style.css"

    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_header():
    """Render page header"""
    st.markdown(
        "<h1><span>🎵</span> Billboard Year-End Top 100 Dashboard</h1>",
        unsafe_allow_html=True,
    )
