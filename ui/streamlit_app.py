import streamlit as st
import websockets
import asyncio
import json
import re
from datetime import datetime
import time

async def get_bot_response(message):
    """Get response from WebSocket with proper connection handling"""
    uri = "ws://localhost:8000/ws/chat"
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
            full_response = ""
            try:
                while True:
                    msg = await websocket.recv()
                    if msg == "[END]":
                        break
                    full_response += msg + " "
            except websockets.ConnectionClosed:
                pass
            return full_response.strip()
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return "Sorry, I couldn't connect to the news service. Please try again."

def format_message_content(content, is_assistant=False):
    """Format message content with enhanced styling"""
    if not is_assistant:
        return content
    
    # Clean up the content
    content = content.replace('**', '')
    
    # Format based on content type
    formatted = ""
    
    # Split content by numbers and format each item
    if re.search(r'\d+\.', content):
        # First add any header text before the numbered list
        header_match = re.match(r'^(.*?)(?=1\.)', content, re.DOTALL)
        if header_match and header_match.group(1).strip():
            formatted += f'<div class="news-header-item">{header_match.group(1).strip()}</div>'
        
        # Then process the numbered items
        items = re.split(r'(\d+\. )', content)[1:]  # Split by numbers but keep them
        for i in range(0, len(items), 2):
            if i+1 < len(items):
                number = items[i]
                text = items[i+1].strip()
                formatted += f'<div class="news-item"><div class="number">{number}</div><div class="news-text">{text}</div></div>'
    else:
        # Default formatting for non-numbered content
        formatted = f'<div class="news-detail">{content}</div>'
    
    return formatted

def main():
    # Set page config
    st.set_page_config(
        page_title="📰 News Assistant Pro",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Update the CSS styles for a more aesthetic look
    st.markdown("""
        <style>
        /* Global Styles */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .main {
            background-color: #f8f9fa;
            font-family: 'Inter', sans-serif;
        }
        
        /* Chat Container */
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #f0f0f0;  /* Light grey background */
            border-radius: 20px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
        }
        
        /* Message Styles */
        .chat-message {
            padding: 1.8rem;
            border-radius: 15px;
            margin-bottom: 1.8rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 0, 0, 0.05);
            background-color: white;  /* Keep messages white for contrast */
        }
        
        .user-message {
            background: linear-gradient(145deg, #000000, #1a1a1a);
            color: white;
            border-left: none;
            margin-left: 50px;
            margin-right: 0;
        }
        
        .bot-message {
            background-color: white;
            border-left: 4px solid #000000;
            color: #000000;
            margin-right: 50px;
            margin-left: 0;
        }
        
        /* News Items */
        .news-item {
            padding: 18px 20px;
            margin: 15px 0;
            background-color: white;
            border-radius: 12px;
            border-left: 3px solid #000000;
            display: flex;
            align-items: flex-start;
            gap: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }
        
        .news-item:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        }
        
        .number {
            color: #000000;
            font-weight: 700;
            min-width: 30px;
            flex-shrink: 0;
            font-size: 1.1rem;
        }
        
        .news-text {
            flex: 1;
            line-height: 1.7;
            color: #1a1a1a;
            font-size: 1.05rem;
        }
        
        /* Headers */
        .news-header-item {
            font-size: 1.2rem;
            font-weight: 600;
            color: #000000;
            margin: 25px 0 20px 0;
            padding: 10px 0;
            border-bottom: 2px solid rgba(0, 0, 0, 0.1);
        }
        
        /* Message Names */
        .chat-message b {
            display: inline-block;
            margin-bottom: 12px;
            font-size: 1.1rem;
            letter-spacing: 0.3px;
        }
        
        .bot-message b {
            color: #000000;
            padding: 5px 10px;
            border-radius: 8px;
            background: rgba(0, 0, 0, 0.05);
        }
        
        .user-message b {
            color: #ffffff;
            padding: 5px 10px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
        }
        
        /* Input Box */
        .stTextInput input {
            background-color: white;
            border: 2px solid rgba(0, 0, 0, 0.1);
            border-radius: 12px;
            padding: 1rem 1.2rem;
            font-size: 1.05rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput input:focus {
            border-color: #000000;
            box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Refresh Button */
        .stButton button {
            background: #000000;
            color: white;
            border: none;
            padding: 0.8rem 1.8rem;
            border-radius: 12px;
            font-weight: 500;
            letter-spacing: 0.3px;
            transition: all 0.3s ease;
            text-transform: uppercase;
            font-size: 0.9rem;
        }
        
        .stButton button:hover {
            background: #1a1a1a;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Loading Spinner */
        .stSpinner > div {
            border-width: 3px;
            border-color: #000000 !important;
            border-right-color: transparent !important;
        }
        
        .stSpinner + div {
            color: #000000 !important;
            font-weight: 500;
            letter-spacing: 0.3px;
        }
        
        /* Today's Headlines Section */
        .today-headlines {
            margin-top: 30px;
            padding: 20px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        
        /* Add container padding */
        .element-container {
            padding: 0.5rem;
        }
        
        /* Style the chat input container */
        .stChatInputContainer {
            background-color: #f0f0f0;
            padding: 1rem;
            border-radius: 15px;
            margin-top: 1rem;
        }
        
        /* Refresh button container */
        .refresh-button-container {
            background-color: #f0f0f0;
            padding: 1rem;
            border-radius: 15px;
            margin-top: 1rem;
            text-align: center;
        }
        
        /* Header Styles */
        .news-header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(145deg, #000000, #1a1a1a);
            color: white;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .news-header h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            font-weight: 700;
            color: white;
        }
        
        .news-header p {
            font-size: 1.1rem;
            opacity: 0.9;
            color: white;
        }
        
        /* Title container */
        .title-container {
            background: linear-gradient(145deg, #000000, #1a1a1a);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .title-container h1 {
            color: white;
            font-size: 2rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .title-container p {
            color: rgba(255, 255, 255, 0.9);
            margin: 0.5rem 0 0 0;
            font-size: 1.1rem;
        }
        
        /* Spinner container */
        .stSpinner {
            text-align: center;
            padding: 1rem;
        }
        
        /* Spinner text */
        .stSpinner + div {
            color: #000000 !important;
            font-weight: 500;
            font-size: 1.1rem;
            margin-top: 0.5rem;
            text-align: center;
            display: block !important;
            visibility: visible !important;
        }
        
        /* Question category styling */
        .question-category {
            margin-bottom: 2rem;
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .question-category h3 {
            color: #000000;
            font-size: 1.1rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(0, 0, 0, 0.1);
            font-weight: 600;
        }
        
        .question-category ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .question-category li {
            color: #000000;
            padding: 0.8rem;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.2s ease;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .question-category li:hover {
            background-color: #f8f9fa;
            transform: translateX(5px);
            border-color: rgba(0, 0, 0, 0.1);
        }
        
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        
        .sidebar h3 {
            color: #000000;
            font-size: 1.1rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid rgba(0, 0, 0, 0.1);
        }
        
        .sidebar ul {
            list-style: none;
            padding-left: 0;
        }
        
        .sidebar li {
            margin-bottom: 0.8rem;
            color: #000000;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .sidebar li:hover {
            transform: translateX(5px);
        }
        </style>
    """, unsafe_allow_html=True)

    # Update the header markup
    st.markdown("""
        <div class="title-container">
            <h1>📰 News Assistant Pro</h1>
            <p>Your personal AI-powered news companion</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar with updated questions
    with st.sidebar:
        st.markdown("""
        <div style='background: #000000; padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;'>
            <h2 style='color: white; margin: 0; font-size: 1.5rem; font-weight: 600;'>💡 Quick Questions</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # General News Section
        st.markdown("### 📰 General News Updates")
        st.markdown("- 📍 What are today's top headlines?")
        st.markdown("- 📋 Give me a bullet-point summary of today's news")
        st.markdown("- 🌍 What are the major events happening today?")
        st.markdown("- 📊 List the most important news stories")
        
        # Technology News Section
        st.markdown("### 💻 Technology News")
        st.markdown("- 🔧 What are the latest tech updates?")
        st.markdown("- 📱 Show me today's technology headlines")
        st.markdown("- 🚀 What's new in the tech world?")
        
        # Business News Section
        st.markdown("### 💰 Business News")
        st.markdown("- 📈 What are the top business stories today?")
        st.markdown("- 🏢 Tell me about today's market news")
        st.markdown("- 💼 What's happening in the business world?")
        
        # Sports News Section
        st.markdown("### 🏆 Sports News")
        st.markdown("- ⚽ What are the latest sports updates?")
        st.markdown("- 🏏 Show me today's sports headlines")
        st.markdown("- 🎯 What's happening in sports today?")

    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        css_class = "user-message" if message["role"] == "user" else "bot-message"
        name = 'You' if message["role"] == "user" else '🤖 News Assistant'
        
        content = format_message_content(
            message["content"], 
            is_assistant=(message["role"] == "assistant")
        )
        
        st.markdown(f"""
            <div class="chat-message {css_class}">
                <b>{name}</b><br>
                {content}
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Ask me anything about the news..."):
        # First show the user's question
        st.markdown(f"""
            <div class="chat-message user-message">
                <b>You</b><br>
                {prompt}
            </div>
        """, unsafe_allow_html=True)
        
        # Add spinner styles for horizontal text
        st.markdown("""
            <style>
            /* Spinner container */
            .stSpinner {
                text-align: center;
                padding: 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
            }
            
            /* Fix spinner text display */
            .stSpinner > div {
                display: flex !important;
                flex-direction: row !important;
                align-items: center !important;
                gap: 10px !important;
                white-space: nowrap !important;
                color: #000000 !important;
                font-weight: 600 !important;
                font-size: 1.1rem !important;
            }
            
            /* Ensure text stays on one line */
            .stSpinner > div span {
                display: inline-block !important;
                white-space: pre !important;
            }
            
            /* Spinner animation */
            .stSpinner > div:first-child {
                border-color: #000000 !important;
                border-right-color: transparent !important;
                width: 25px !important;
                height: 25px !important;
                margin-right: 10px !important;
            }
            
            /* Force text to be on single line */
            .element-container:has(.stSpinner) {
                display: flex !important;
                justify-content: center !important;
                align-items: center !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Show spinner with text
        with st.spinner("🔍 Searching news..."):
            try:
                # Add a small delay
                time.sleep(1)
                
                # Get the response
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(get_bot_response(prompt))
                loop.close()
                
                # Update session state
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # Show the AI response
                st.markdown(f"""
                    <div class="chat-message bot-message">
                        <b>🤖 News Assistant</b><br>
                        {format_message_content(response, True)}
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error getting response: {str(e)}")

    # Refresh button
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🔄 Refresh Feed"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()