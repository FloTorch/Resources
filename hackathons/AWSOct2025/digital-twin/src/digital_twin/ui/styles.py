"""
Styles for Digital Twin Application
"""

def get_custom_css():
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main Container */
    .main {
        background-color: #ffffff;
        padding: 0;
    }
    
    /* Sidebar Styles */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e5e5;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #ffffff;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hide sidebar toggle buttons to prevent closing */
    button[aria-label*="sidebar"], 
    button[aria-label*="Close"], 
    button[aria-label*="Open"] {
        display: none !important;
    }
    
    /* Sidebar Title */
    .sidebar-title {
        font-size: 24px;
        font-weight: 600;
        color: #202123;
        padding: 20px 16px;
        margin-bottom: 10px;
        text-align: center;
    }
    
    /* Sidebar Buttons */
    [data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: #202123;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        padding: 1px 16px;
        font-size: 14px;
        font-weight: 400;
        text-align: left;
        transition: all 0.2s;
        width: 100%;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #f7f7f8;
        border-color: #10a37f;
    }
    
    [data-testid="stSidebar"] .stButton > button:active {
        background-color: #ececec;
    }
    
    /* Sidebar Text Input (Search) */
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #f7f7f8;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
        color: #202123;
    }
    
    [data-testid="stSidebar"] .stTextInput > div > div > input:focus {
        border-color: #10a37f;
        background-color: #ffffff;
    }
    
    /* Dropdown Styles */
    .stSelectbox {
        margin: 8px 8px;
    }
    
    .stSelectbox > div > div {
        background-color: #ffffff;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        font-size: 14px;
        color: #202123;
    }
    
    /* Chat History Section */
    .chat-history-title {
        font-size: 12px;
        font-weight: 600;
        color: #8e8ea0;
        text-transform: uppercase;
        padding: 20px 16px 8px 16px;
        letter-spacing: 0.5px;
    }
    
    .chat-history-item {
        padding: 12px 16px;
        margin: 4px 8px;
        border-radius: 8px;
        cursor: pointer;
        color: #202123;
        font-size: 14px;
        transition: background-color 0.2s;
    }
    
    .chat-history-item:hover {
        background-color: #f7f7f8;
    }
    
    /* Chat Container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Center Container for New Chat */
    .center-container {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        min-height: 20vh;
        padding: 20px;
        padding-top: 15vh;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        color: #202123;
        margin-top: 80px;
        margin-bottom: 20px;
        text-align: center;
    }
    


    /* Chat Message Styles */
    .chat-message {
        padding: 20px 24px;
        margin-bottom: 12px;
        border-radius: 16px;
        max-width: 70%;
        word-wrap: break-word;
    }
    
    .chat-message.user {
        background-color: #f4f4f4;
        margin-left: auto;
        margin-right: 0;
        border: 1px solid #e5e5e5;
        padding: 10px 16px;
    }

    .chat-message.assistant {
        background-color: #ffffff;
        margin-left: 0;
        margin-right: auto;
        border: 1px solid #e5e5e5;
    }
    
    .message-content {
        color: #202123;
        font-size: 15px;
        line-height: 1.6;
        white-space: pre-wrap;
        word-break: break-word;
    }
    
    /* Enhanced markdown formatting for assistant responses */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #202123;
        font-weight: 600;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
    }
    
    .stMarkdown h1 {
        font-size: 24px;
        border-bottom: 2px solid #e5e5e5;
        padding-bottom: 13px;
    }
    
    .stMarkdown h2 {
        font-size: 20px;
    }
    
    .stMarkdown h3 {
        font-size: 18px;
    }
    
    .stMarkdown ul, .stMarkdown ol {
        padding-left: 24px;
        margin-top: 8px;
        margin-bottom: 8px;
    }
    
    .stMarkdown li {
        margin-bottom: 6px;
        line-height: 1.6;
    }
    
    .stMarkdown p {
        margin-bottom: 12px;
        line-height: 1.6;
    }
    
    .stMarkdown strong {
        font-weight: 600;
        color: #202123;
    }
    
    .stMarkdown code {
        background-color: #f1f3f4;
        padding: 2px 6px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        color: #d73a49;
    }
    
    .stMarkdown a {
        color: #10a37f;
        text-decoration: none;
        font-weight: 500;
    }
    
    .stMarkdown a:hover {
        text-decoration: underline;
    }
    
    /* CRITICAL: Fixed Chat Input Container */
    [data-testid="stChatInputContainer"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background-color: #ffffff !important;
        border-top: 1px solid #e5e5e5 !important;
        padding: 16px 0 !important;
        z-index: 999 !important;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05) !important;
        width: 100% !important;
    }
    
    /* Center the input within fixed container - consistent width */
    [data-testid="stChatInputContainer"] > div {
        max-width: 800px !important;
        width: 800px !important;
        margin: 0 auto !important;
        padding: 0 20px !important;
    }
    
    /* Chat Input Styling */
    .stChatInput {
        background-color: transparent !important;
    }
    
    .stChatInput > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 4px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stChatInput textarea {
        background-color: #ffffff !important;
        border: none !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        color: #202123 !important;
        min-height: 24px !important;
        max-height: 200px !important;
    }
    
    .stChatInput textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stChatInput > div:focus-within {
        border-color: #10a37f !important;
        box-shadow: 0 2px 12px rgba(16, 163, 127, 0.15) !important;
    }
    
    /* Text Input Styling (for other inputs) */
    .stTextInput > div > div > input {
        background-color: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 15px;
        color: #202123;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10a37f;
        box-shadow: 0 2px 12px rgba(16, 163, 127, 0.15);
        outline: none;
    }
    
    /* Main Button Styles */
    .main .stButton > button {
        background-color: #10a37f;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .main .stButton > button:hover {
        background-color: #0d8f6d;
    }
    
    /* Scrollbar Styles */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #ffffff;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }
    
    /* Remove/Adjust Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 120px !important; /* Space for fixed input */
    }
    
    /* Divider */
    .sidebar-divider {
        border-top: 1px solid #e5e5e5;
        margin: 16px 0;
    }
    
    /* Search Modal Input Styling - Match chat input exactly */
    [data-testid="stVerticalBlock"] > div:has(input[placeholder="Type to search your chat history..."]) .stTextInput {
        background-color: transparent !important;
    }
    
    [data-testid="stVerticalBlock"] > div:has(input[placeholder="Type to search your chat history..."]) .stTextInput > div {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 4px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
    }
    
    [data-testid="stVerticalBlock"] > div:has(input[placeholder="Type to search your chat history..."]) .stTextInput > div > div > input {
        background-color: #ffffff !important;
        border: none !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        color: #202123 !important;
        min-height: 24px !important;
        max-height: 200px !important;
        text-align: left !important;
    }
    
    [data-testid="stVerticalBlock"] > div:has(input[placeholder="Type to search your chat history..."]) .stTextInput > div > div > input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    [data-testid="stVerticalBlock"] > div:has(input[placeholder="Type to search your chat history..."]) .stTextInput > div:focus-within {
        border-color: #10a37f !important;
        box-shadow: 0 2px 12px rgba(16, 163, 127, 0.15) !important;
    }
    
    /* Left align placeholder text */
    [data-testid="stVerticalBlock"] > div:has(input[placeholder="Type to search your chat history..."]) .stTextInput > div > div > input::placeholder {
        text-align: left !important;
    }
    
    /* Chat history items hover effect */
    .chat-history-item:hover {
        background-color: #f0f0f0 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Back button styling - reduce padding and width */
    button[key="back"] {
        padding: 6px 12px !important;
        width: auto !important;
        min-width: auto !important;
        max-width: 120px !important;
    }
    
    /* Style chat history buttons to look like simple text */
    button[key^="search_chat_"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 8px 0 !important;
        margin: 2px 0 !important;
        text-align: left !important;
        color: #202123 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: auto !important;
        min-width: auto !important;
        max-width: none !important;
    }
    
    button[key^="search_chat_"]:hover {
        background-color: #f8f9fa !important;
        border-radius: 4px !important;
    }
    
    /* Style error messages to match search bar message */
    .stAlert {
        background-color: #f8f9fa !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 6px !important;
        color: #8e8ea0 !important;
        font-size: 12px !important;
        padding: 8px 12px !important;
        margin: 0 auto !important;
        width: fit-content !important;
    }
    
    /* Search Modal Close Button */
    button[kind="secondary"]:has-text("✕") {
        background-color: transparent !important;
        border: none !important;
        color: #8e8ea0 !important;
        font-size: 20px !important;
        padding: 4px 8px !important;
    }
    
    /* Style sidebar buttons - more specific targeting */
    [data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        font-size: 14px !important;
        text-align: left !important;
        padding: 8px 16px !important;
        justify-content: flex-start !important;
        display: flex !important;
        align-items: center !important;
    }
    
    /* Target specific buttons by key */
    [data-testid="stSidebar"] button[key="new_chat_button_2024"] {
        font-size: 14px !important;
        text-align: left !important;
        padding: 8px 16px !important;
        justify-content: flex-start !important;
    }
    
    [data-testid="stSidebar"] button[key="search_btn"] {
        font-size: 14px !important;
        text-align: left !important;
        padding: 8px 16px !important;
        justify-content: flex-start !important;
    }
    
    </style>
    """