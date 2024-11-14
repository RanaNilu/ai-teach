import streamlit as st
import os
import sys
import subprocess
from datetime import datetime
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Dependency management
REQUIRED_LIBRARIES = ["scikit-learn"]

def install_and_import(libraries):
    for lib in libraries:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_and_import(REQUIRED_LIBRARIES)

# Streamlit settings
st.set_page_config(page_title="AI Teaching Assistant", layout="wide")

# Session state for managing content and chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'course_content' not in st.session_state:
    st.session_state.course_content = {}
if 'vectorizer' not in st.session_state:
    st.session_state.vectorizer = TfidfVectorizer()

def save_course_content(course_name, content):
    with open(f"{course_name}_content.json", 'w') as f:
        json.dump(content, f)

def load_course_content(course_name):
    if os.path.exists(f"{course_name}_content.json"):
        with open(f"{course_name}_content.json", 'r') as f:
            return json.load(f)
    return []

def save_chat_history():
    with open('chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f)

def load_chat_history():
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            st.session_state.chat_history = json.load(f)

# Sidebar navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.selectbox("Select Mode", ["Course Management", "Student Chat"])

# Course Management Section
if menu_option == "Course Management":
    st.title("Upload and Manage Course Content")
    
    course_name = st.text_input("Course Name")
    uploaded_file = st.file_uploader("Upload course content (text file)", type="txt")

    if st.button("Upload Content") and course_name and uploaded_file:
        content = uploaded_file.read().decode("utf-8").splitlines()
        st.session_state.course_content[course_name] = content
        save_course_content(course_name, content)
        st.success(f"Content for '{course_name}' uploaded successfully!")

    # Display uploaded course contents
    st.subheader("Available Courses")
    for course, contents in st.session_state.course_content.items():
        with st.expander(course):
            for line in contents:
                st.write(f"- {line}")

# Student Chat Section
elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")
    
    load_chat_history()
    load_course_content("course_name")

    # Select course to chat about
    course_name = st.selectbox("Select Course", list(st.session_state.course_content.keys()))
    content = st.session_state.course_content.get(course_name, [])
    
    # TF-IDF processing for the selected course
    if content:
        tfidf_matrix = st.session_state.vectorizer.fit_transform(content)
    
        user_question = st.text_input("Ask your question:")

        if st.button("Send"):
            if user_question:
                # Log user message
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({"time": timestamp, "user": user_question})
                
                # Generate AI response based on content
                user_tfidf = st.session_state.vectorizer.transform([user_question])
                similarity_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
                best_match_index = similarity_scores.argmax()
                
                if similarity_scores[best_match_index] > 0:
                    ai_response = content[best_match_index]
                else:
                    ai_response = "I'm sorry, I don't have information on that question."

                st.session_state.chat_history.append({"time": timestamp, "ai": ai_response})
                save_chat_history()

    # Display chat history
    st.subheader("Chat History")
    for chat in st.session_state.chat_history:
        if "user" in chat:
            st.write(f"Student [{chat['time']}]: {chat['user']}")
        elif "ai" in chat:
            st.write(f"AI Teacher [{chat['time']}]: {chat['ai']}")

# Footer
st.markdown("---")
st.markdown("Powered by Streamlit")
