import streamlit as st
import pathlib


def load_css():
    """Load custom CSS styling"""
    script_dir = pathlib.Path(__file__).parent.parent
    css_path = script_dir / "style.css"

    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
