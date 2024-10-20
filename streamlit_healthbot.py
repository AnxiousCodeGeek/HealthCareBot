import os
import sqlite3
from groq import Groq
from datetime import datetime
import streamlit as st

# Initialize the Groq client with the API key
api_key = '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'  # Replace with your actual API key
client = Groq(api_key=api_key)

drive_folder_path = '/home/ncai-scl/chatbot/healthcare_chatbot_dashboard/databases'  # Update this path to your desired local directory

def setup_database():
    # Create a timestamp for the database filename
    timestamp = datetime.now().strftime('%m-%d-%y_%H-%M-%S')
    db_file_name = f"chat_history_{timestamp}.db"
    conn = sqlite3.connect(os.path.join(drive_folder_path, db_file_name))
    cursor = conn.cursor()
    # Drop the chat_history table if it exists
    cursor.execute("DROP TABLE IF EXISTS chat_history")
    # Create a new table for chat history with the new schema
    cursor.execute('''
        CREATE TABLE chat_history (
            id INTEGER PRIMARY KEY,
            user_message TEXT,
            bot_response TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    return conn, db_file_name

def get_chat_response(user_message):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": user_message,
            }
        ],
        model="llama-3.2-3b-preview",
    )
    return chat_completion.choices[0].message.content

def low_bandwidth_response(user_message):
    if len(user_message) > 100:
        user_message = user_message[:100]  # Limit to 100 characters
    response = get_chat_response(user_message)
    return response

def healthcare_chatbot():
    # Set up the SQLite database
    conn, db_file_name = setup_database()
    
    # Add an icon at the top without a caption
    icon_path = "/home/ncai-scl/chatbot/healthcare_chatbot_dashboard/chatbot.png"  # Replace with your icon path
    col1, col2, col3 = st.columns([1, 3, 7])  # Wider center column for more space
    with col3:
        st.image(icon_path, width=150)  # Display the icon without caption

    # Add the title below the icon
    st.markdown("<h2 style='text-align: center; color: #ffffff;'>HealthCare Assistant</h2>", unsafe_allow_html=True)
    
    # Set the title next to the icon
    # st.markdown("<h1 style='display: inline; color: #000000;'>Healthcare Chatbot</h1>", unsafe_allow_html=True)

    st.write("Welcome to the Healthcare Chatbot! I will try my best to answer your health-related queries.")

    # Initialize session state for chat sessions if not already done
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}
        st.session_state.current_chat_id = None

    # Dropdown for selecting existing chat sessions
    chat_session_names = list(st.session_state.chat_sessions.keys())
    chat_session_names.append("New Chat")  # Add option for new chat
    selected_chat = st.selectbox("Select Chat Session:", chat_session_names)

    # Handle user input for creating new chat sessions
    user_input = st.text_input("Chat name: (The chat name refers to what conversation you will be having about with the Bot)", "")
    
    if selected_chat == "New Chat" and user_input:
        # Use the first word from the user input as the tab name
        first_health_word = user_input.split()[0] if user_input else "General"
        chat_id = f"{first_health_word}"
        
        # Initialize a new chat session if it doesn't already exist
        if chat_id not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[chat_id] = []
        
        st.session_state.current_chat_id = chat_id  # Set current chat ID for new messages

        # Display a message to indicate a new chat has started
        st.success(f"New chat session '{chat_id}' created!")

    # Display chat history if an existing chat is selected
    if selected_chat != "New Chat":
        st.write(f"**Chat History for '{selected_chat}':**")

        # Check if current_chat exists in session state before accessing
        if selected_chat in st.session_state.chat_sessions:
            # Display each message in a styled box
            for sender, message in st.session_state.chat_sessions[selected_chat]:
                if sender == "You":
                    st.markdown(f"""
                        <div style="background-color: #D1E7DD; border-radius: 10px; padding: 10px; margin: 5px; text-align: right; color: black;">
                            <strong>{sender}:</strong> {message}
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="background-color: #CFE2FF; border-radius: 10px; padding: 10px; margin: 5px; text-align: left; color: black;">
                            <strong>{sender}:</strong> {message}
                        </div>
                    """, unsafe_allow_html=True)

            # Create a text input for user messages
            user_message = st.text_input("Type your message here:", key=f"input_{selected_chat}")

            if st.button("Send", key=f"send_{selected_chat}"):
                if user_message.lower() == 'exit':
                    response = "Session ended."
                else:
                    # Simulate bot response
                    response = low_bandwidth_response(user_message)

                # Store messages in the current chat session
                st.session_state.chat_sessions[selected_chat].append(("You", user_message))
                st.session_state.chat_sessions[selected_chat].append(("Bot", response))

                # Display the latest messages after sending
                for sender, message in st.session_state.chat_sessions[selected_chat]:
                    if sender == "You":
                        st.markdown(f"""
                            <div style="background-color: #D1E7DD; border-radius: 10px; padding: 10px; margin: 5px; text-align: right; color: black;">
                                <strong>{sender}:</strong> {message}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div style="background-color: #CFE2FF; border-radius: 10px; padding: 10px; margin: 5px; text-align: left; color: black;">
                                <strong>{sender}:</strong> {message}
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.write("No chat history available for this session.")

    conn.close()  # Close the database connection



# Start the chatbot session
if __name__ == "__main__":
    healthcare_chatbot()
