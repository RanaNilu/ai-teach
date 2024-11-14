import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import json
import os

# File paths for storing data permanently
COURSE_CONTENT_FILE = 'course_content.json'
CHAT_HISTORY_FILE = 'chat_history.json'

# Initialize Streamlit page
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_content' not in st.session_state:
    st.session_state.uploaded_content = {}

# Load course content from file
def load_course_content():
    if os.path.exists(COURSE_CONTENT_FILE):
        with open(COURSE_CONTENT_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save course content to file
def save_course_content():
    with open(COURSE_CONTENT_FILE, 'w') as f:
        json.dump(st.session_state.uploaded_content, f)

# Load chat history from file
def load_chat_history():
    if os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'r') as f:
            st.session_state.chat_history = json.load(f)

# Save chat history to file
def save_chat_history():
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(st.session_state.chat_history, f)

# Parse uploaded file content
def parse_uploaded_content(file_content):
    content = file_content.decode('utf-8')
    return [line.strip() for line in content.splitlines() if line.strip()]  # Each line is treated as content

# Find the most relevant answer using TF-IDF and cosine similarity
def find_most_relevant_answer(question, course_content):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([question] + course_content)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    best_match_idx = cosine_similarities.argmax()
    if cosine_similarities[best_match_idx] > 0:  # Ensure there is a meaningful match
        return course_content[best_match_idx]
    return "Sorry, I couldn't find an exact match. Please check the content or rephrase your question."

# Load data at the start of the app
st.session_state.uploaded_content = load_course_content()
load_chat_history()

# Sidebar Navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.selectbox(
    "Select Mode",
    ["Course Management", "Student Chat", "Resource Center"]
)

# Course Management
if menu_option == "Course Management":
    st.title("Course Management")

    # Display uploaded content
    st.subheader("Uploaded Courses")
    for course, content in st.session_state.uploaded_content.items():
        with st.expander(course):
            for topic in content:
                st.write(f"- {topic}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")

    # Select course
    selected_course = st.selectbox("Select Course", list(st.session_state.uploaded_content.keys()))
    
    # Chat interface
    user_message = st.text_input("Ask your question:")
    if st.button("Send"):
        if user_message and selected_course in st.session_state.uploaded_content:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            course_content = st.session_state.uploaded_content[selected_course]
            response = find_most_relevant_answer(user_message, course_content)
            
            # Save chat history
            st.session_state.chat_history.append({
                "timestamp": timestamp,
                "user": user_message,
                "response": response,
                "course": selected_course
            })
            save_chat_history()
            
            # Display response
            st.write(f"Teacher: {response}")

    # Display chat history
    st.subheader("Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.text(f"[{chat['timestamp']}] {chat['course']}")
        st.text(f"Student: {chat['user']}")
        st.text(f"Teacher: {chat['response']}")
        st.text("---")

else:  # Resource Center
    st.title("Resource Center")

    # Upload learning materials
    st.subheader("Upload Learning Materials")
    uploaded_file = st.file_uploader("Choose a file (TXT format)")
    if uploaded_file is not None:
        try:
            course_name = uploaded_file.name.split('.')[0]
            parsed_content = parse_uploaded_content(uploaded_file.read())
            st.session_state.uploaded_content[course_name] = parsed_content
            save_course_content()  # Save permanently
            st.success(f"Uploaded and saved content for: {course_name}")
        except Exception as e:
            st.error(f"Failed to process the uploaded file: {e}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and TF-IDF")
