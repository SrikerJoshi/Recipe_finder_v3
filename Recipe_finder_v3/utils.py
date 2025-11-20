import ipinfo
import streamlit as st

def get_user_location(ipinfo_token):
    try:
        handler = ipinfo.getHandler(ipinfo_token)
        details = handler.getDetails()
        location = details.loc.split(",")  # lat, long
        return float(location[0]), float(location[1])
    except Exception as e:
        st.error(f"Could not determine location: {e}")
        return 0.0, 0.0

def inject_custom_css(css_file_path):
    with open(css_file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
