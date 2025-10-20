"""
Sidebar Component for Digital Twin Application
"""
import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def render_sidebar(service):
    """Render the sidebar with all components"""
    with st.sidebar:
        st.markdown('<div class="sidebar-title">DIGITAL TWIN</div>', unsafe_allow_html=True)
        
        if service is None:
            st.warning("Backend unavailable")
            return None
        
        if st.button("New chat", key="new_chat_button_2024", use_container_width=True):
            if not st.session_state.get('selected_company_key'):
                st.markdown('<p style="color: #8e8ea0; font-size: 12px; text-align: center; padding: 8px 12px; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e5e5e5; margin: 0 auto; width: fit-content;">Please select a company first!</p>', unsafe_allow_html=True)
                st.rerun()
                return None
            
            st.session_state.messages = []
            st.session_state.chat_started = False
            st.session_state.current_chat = None
            st.session_state.current_session_id = None
            st.session_state.needs_response = False
            st.session_state.show_search = False
            st.rerun()
            
            return st.session_state.get('selected_company_key')
        
        if "show_search" not in st.session_state:
            st.session_state.show_search = False
        
        if st.button("Search chats", key="search_btn", use_container_width=True):
            st.session_state.show_search = not st.session_state.show_search
            st.rerun()
        
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        # Industry and company selection
        st.markdown("**Select Industry**")
        
        if 'selected_industry' not in st.session_state:
            st.session_state.selected_industry = None
        
        industries = service.get_industries()
        
        current_industry_index = 0
        if st.session_state.selected_industry and st.session_state.selected_industry in industries:
            current_industry_index = industries.index(st.session_state.selected_industry) + 1
        
        selected_industry = st.selectbox(
            "Industry",
            options=["Select an industry"] + industries,
            index=current_industry_index,
            key="industry_select",
            label_visibility="collapsed"
        )
        
        if selected_industry != "Select an industry":
            if st.session_state.selected_industry != selected_industry:
                st.session_state.selected_industry = selected_industry
                st.session_state.selected_company_key = None
                st.rerun()
        else:
            st.session_state.selected_industry = None
            st.session_state.selected_company_key = None
        
        if st.session_state.selected_industry:
            st.markdown("**Select Company**")
            
            companies = service.get_companies_by_industry(st.session_state.selected_industry)
            company_options = {c['name']: c['key'] for c in companies}
            
            current_company_index = 0
            if st.session_state.selected_company_key:
                current_company_name = next(
                    (name for name, key in company_options.items() 
                     if key == st.session_state.selected_company_key),
                    None
                )
                if current_company_name and current_company_name in list(company_options.keys()):
                    current_company_index = list(company_options.keys()).index(current_company_name) + 1
            
            selected_company = st.selectbox(
                "Company",
                options=["Select a company"] + list(company_options.keys()),
                index=current_company_index,
                key="company_select",
                label_visibility="collapsed"
            )
            
            if selected_company != "Select a company":
                new_company_key = company_options[selected_company]
                if st.session_state.selected_company_key != new_company_key:
                    st.session_state.selected_company_key = new_company_key
                    st.rerun()
            else:
                st.session_state.selected_company_key = None
        
        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        # Chat history section
        st.markdown('<div class="chat-history-title">CHAT HISTORY</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <style>
        div[data-testid="column"] button[kind="secondary"] {
            height: 40px !important;
            min-height: 40px !important;
            max-height: 40px !important;
        }
        
        button[kind="secondary"][data-testid="baseButton-secondary"] {
            height: 40px !important;
            min-height: 40px !important;
            max-height: 40px !important;
        }
        
        div[data-testid="column"]:nth-child(2) button {
            height: 40px !important;
            min-height: 40px !important;
            max-height: 40px !important;
        }
        
        div[data-testid="column"]:nth-child(2) button {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        sessions_result = service.list_user_sessions(limit=10)
        
        if sessions_result.get('success') and sessions_result.get('sessions'):
            for session in sessions_result['sessions']:
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    session_title = session.get('session_title', 'Untitled')[:19] + "..."
                    if st.button(
                        session_title,
                        key=f"chat_{session['session_id']}",
                        use_container_width=True,
                        type="secondary"
                    ):
                        history = service.get_session_history(session['session_id'])
                        
                        if history.get('success'):
                            from src.digital_twin.ui.utils import load_session_messages
                            st.session_state.messages = load_session_messages(session['session_id'])
                            st.session_state.chat_started = True
                            st.session_state.current_session_id = session['session_id']
                            st.session_state.selected_company_key = session.get('company_key')
                            st.rerun()
                
                with col2:
                    if st.button("⋮", key=f"menu_{session['session_id']}", help="Options", type="secondary"):
                        st.session_state[f"show_menu_{session['session_id']}"] = True
                        st.rerun()
                
                if st.session_state.get(f"show_menu_{session['session_id']}", False):
                    col_del, col_cancel = st.columns([1, 1])
                    
                    with col_del:
                        if st.button("Delete", key=f"delete_{session['session_id']}", help="Delete this session", type="secondary", use_container_width=True):
                            delete_result = service.delete_session(session['session_id'])
                            if delete_result.get('success'):
                                st.success("Session deleted!")
                                if st.session_state.current_session_id == session['session_id']:
                                    st.session_state.current_session_id = None
                                    st.session_state.messages = []
                                    st.session_state.chat_started = False
                                del st.session_state[f"show_menu_{session['session_id']}"]
                                st.rerun()
                            else:
                                st.error(f"Failed to delete: {delete_result.get('error', 'Unknown error')}")
                    
                    with col_cancel:
                        if st.button("Cancel", key=f"cancel_{session['session_id']}", help="Cancel delete", type="secondary", use_container_width=True):
                            del st.session_state[f"show_menu_{session['session_id']}"]
                            st.rerun()
        else:
            st.markdown('<p style="color: #8e8ea0; font-size: 12px; padding: 8px;">No chat history yet</p>', unsafe_allow_html=True)
    
    return st.session_state.get('selected_company_key')

