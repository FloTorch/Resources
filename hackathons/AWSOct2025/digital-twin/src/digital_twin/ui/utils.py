"""UI utilities for session management."""

import streamlit as st
import re


def load_session_messages(session_id):
    """Load messages for a specific session."""
    if 'session_messages' not in st.session_state:
        st.session_state.session_messages = {}
    
    if session_id not in st.session_state.session_messages:
        st.session_state.session_messages[session_id] = []
    
    return st.session_state.session_messages[session_id]


def save_message_to_session(session_id, role, content):
    """Save a message to the current session."""
    if 'session_messages' not in st.session_state:
        st.session_state.session_messages = {}
    
    if session_id not in st.session_state.session_messages:
        st.session_state.session_messages[session_id] = []
    
    st.session_state.session_messages[session_id].append({
        "role": role,
        "content": content
    })


def clean_html_tags(text: str) -> str:
    """Remove HTML tags and entities from text."""
    if not text:
        return text
    
    clean_text = re.sub(r'</?[a-zA-Z][^>]*/?>', '', text)
    clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)
    clean_text = re.sub(r'&#[0-9]+;', '', clean_text)
    clean_text = re.sub(r'&#x[0-9a-fA-F]+;', '', clean_text)
    
    return clean_text.strip()


def format_agent_response(response_text: str) -> str:
    """Clean HTML tags from agent response."""
    return clean_html_tags(response_text)


def initialize_service():
    """Initialize the Digital Twin Service."""
    if 'digital_twin_service' not in st.session_state:
        try:
            with st.spinner("Initializing backend service..."):
                import sys
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                
                from src.digital_twin.core.service import DigitalTwinService
                st.session_state.digital_twin_service = DigitalTwinService()
                st.session_state.service_error = None
        except Exception as e:
            st.session_state.digital_twin_service = None
            st.session_state.service_error = str(e)
            st.error(f"""
            **Backend Service Unavailable**
            
            The backend service could not be initialized. This is likely due to missing dependencies:
            - `strands` (AI Agent Framework)
            - `flotorch` (Flotorch Strands integration)
            
            **Error:** {str(e)}
            
            **To fix:** Contact your backend team for the correct package installation instructions.
            
            **The UI is ready, but backend features won't work until these packages are installed.**
            """)
    return st.session_state.digital_twin_service

