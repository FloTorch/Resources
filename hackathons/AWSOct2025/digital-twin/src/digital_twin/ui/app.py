"""
Digital Twin - Streamlit Application
"""
import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.digital_twin.ui.styles import get_custom_css
from src.digital_twin.ui.sidebar import render_sidebar
from src.digital_twin.ui.utils import initialize_service, load_session_messages, save_message_to_session, clean_html_tags


def display_chat_messages():
    """Display all chat messages in normal order (oldest to newest)"""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            with st.container():
                st.markdown(f"""
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 16px;">
                        <div class="chat-message user">
                            <div class="message-content">{content}</div>
                        </div>
        </div>
        """, unsafe_allow_html=True)
        else:
            with st.container():
                clean_content = clean_html_tags(content)
                st.markdown(f"""
                    <div style="margin-bottom: 20px; padding: 20px; background-color: #f8f9fa; border-radius: 12px; border-left: 4px solid #10a37f;">
                        {clean_content}
        </div>
        """, unsafe_allow_html=True)
        
def handle_user_input(user_input: str, service):
    """Process user input and mark for processing"""
    if service is None:
        st.error("Backend service is not available. Please check the error message above.")
        return
    
    if not st.session_state.get('selected_company_key'):
        st.markdown('<p style="color: #8e8ea0; font-size: 12px; text-align: center; padding: 8px 12px; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e5e5e5; margin: 0 auto; width: fit-content;">Please select a company first.</p>', unsafe_allow_html=True)
        return

    if not user_input.strip():
        st.toast("Please enter at least 1 characters")
        return
    
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    st.session_state.chat_started = True
    st.session_state.needs_response = True
    
    st.rerun()
        

def generate_response(service):
    """Generate response for the last user message"""
    if not st.session_state.messages:
        return
    
    last_message = st.session_state.messages[-1]
    if last_message["role"] != "user":
        return
    
    user_input = last_message["content"]
    
    if not st.session_state.current_session_id:
        with st.spinner("Creating new session..."):
            try:
                session_result = service.create_new_session(
                    st.session_state.selected_company_key,
                    user_input
                )
                
                if not session_result.get('success'):
                    error_msg = session_result.get('error', 'Unknown error')
                    st.error(f"Failed to create session: {error_msg}")
                    st.info(f"Company: {st.session_state.selected_company_key}")
                    st.session_state.needs_response = False
                    return
                    
                st.session_state.current_session_id = session_result['session_id']
            except Exception as e:
                st.error(f"Exception creating session: {str(e)}")
                st.info(f"Company selected: {st.session_state.selected_company_key}")
                st.session_state.needs_response = False
                return
        
        save_message_to_session(st.session_state.current_session_id, "user", user_input)
    else:
        save_message_to_session(st.session_state.current_session_id, "user", user_input)
    
    with st.spinner("Fetching from knowledge base..."):
        try:
            response = service.process_query(
                company_key=st.session_state.selected_company_key,
                user_query=user_input,
                session_id=st.session_state.current_session_id
            )
            
            if response.get('success') or 'response' in response:
                raw_response = response.get('response', response.get('error', 'No response'))
                assistant_response = clean_html_tags(raw_response)
            else:
                error_detail = response.get('error', 'An error occurred')
                assistant_response = f"Error: {error_detail}\n\n**Debug Info:**\n- Company: {st.session_state.selected_company_key}\n- Session ID: {st.session_state.current_session_id}"
        except Exception as e:
            assistant_response = f"Exception during query: {str(e)}\n\n**Debug Info:**\n- Company: {st.session_state.selected_company_key}\n- Session ID: {st.session_state.current_session_id}\n- Query: {user_input}"
        
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_response
        })
        save_message_to_session(st.session_state.current_session_id, "assistant", assistant_response)
        
        st.session_state.needs_response = False
        
        st.rerun()
                        

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="Digital Twin",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    service = initialize_service()
    
    if service is None:
        st.stop()
    
    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False
    
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
    
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None
    
    if "selected_industry" not in st.session_state:
        st.session_state.selected_industry = None
    
    if "selected_company_key" not in st.session_state:
        st.session_state.selected_company_key = None
    
    if "needs_response" not in st.session_state:
        st.session_state.needs_response = False
    
    if "create_new_session" not in st.session_state:
        st.session_state.create_new_session = False
    
    if st.session_state.create_new_session:
        st.session_state.create_new_session = False
        
        with st.spinner("Creating new session..."):
            try:
                session_result = service.create_new_session(
                    st.session_state.selected_company_key,
                    "New chat session"
                )
                
                if session_result.get('success'):
                    st.session_state.current_session_id = session_result['session_id']
                    st.success("New chat session created! Start typing your message.")
                    st.rerun()
                else:
                    error_msg = session_result.get('error', 'Unknown error')
                    st.error(f"Failed to create session: {error_msg}")
                    
            except Exception as e:
                st.error(f"Exception creating session: {str(e)}")
    
    selected_company_key = render_sidebar(service)
    
    # Search page functionality
    if st.session_state.get("show_search", False):
        st.markdown("""
            <div style="text-align: center; padding: 20px 0 40px 0;">
                <h1 style="color: #202123; font-size: 28px; font-weight: 600; margin-bottom: 8px;">Search Your Chats</h1>
                <p style="color: #8e8ea0; font-size: 16px;">Find and access your conversation history</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            search_text = st.text_input(
                "Search chats", 
                placeholder="Type to search your chat history...",
                key="search_input",
                label_visibility="collapsed"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        sessions_result = service.list_user_sessions(limit=20)
        all_sessions = sessions_result.get('sessions', []) if sessions_result.get('success') else []
        
        if search_text:
            matched = [s for s in all_sessions if search_text.lower() in s.get("session_title", "").lower()]
            if matched:
                st.markdown(f"**Search Results ({len(matched)})**")
            else:
                st.info("No chats found. Try a different search term.")
                matched = []
        else:
            matched = all_sessions[:8]
            if matched:
                st.markdown("**Recent Chats**")
            else:
                st.markdown('<p style="color: #8e8ea0; font-size: 12px; text-align: center; padding: 8px 12px; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e5e5e5; margin: 0 auto; width: fit-content;">No chat history yet. Start a new conversation to see it here.</p>', unsafe_allow_html=True)
        
        if matched:
            for session in matched:
                session_title = session.get('session_title', 'Untitled Chat')
                session_id = session.get('session_id', '')
                company_key = session.get('company_key', '')
                created_at = session.get('created_at', '')
                
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    time_str = dt.strftime('%I:%M %p')
                except:
                    time_str = ''
                
                if st.button(
                    session_title,
                    key=f"search_chat_{session_id}",
                    use_container_width=False,
                    type="secondary"
                ):
                    try:
                        history = service.get_session_history(session_id)
                        if history.get('success'):
                            messages = load_session_messages(session_id)
                            st.session_state.messages = messages
                            st.session_state.chat_started = True
                            st.session_state.current_session_id = session_id
                            st.session_state.selected_company_key = company_key
                            st.session_state.show_search = False
                            st.rerun()
                        else:
                            st.error("Failed to load chat")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            if st.button("← Back", key="back", use_container_width=False):
                st.session_state.show_search = False
                st.rerun()
        
        st.stop()
    
    # Main chat interface
    if not st.session_state.chat_started and len(st.session_state.messages) == 0:
        st.markdown("""
            <div class="center-container">
                <div class="welcome-title">What's on your mind today?</div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.5, 3, 0.5])
        with col2:
            user_input = st.chat_input("Ask anything...", key="input_center")
            
            if user_input:
                handle_user_input(user_input, service)
    
    else:
        display_chat_messages()
        
        user_input = st.chat_input("Type your message...", key="input_bottom")
        
        if st.session_state.needs_response:
            generate_response(service)
        
        if user_input:
            handle_user_input(user_input, service)


if __name__ == "__main__":
    main()

