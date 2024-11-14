import streamlit as st
from datetime import datetime
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure Streamlit page
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'course_contents' not in st.session_state:
    st.session_state.course_contents = {}
if 'vectorizer' not in st.session_state:
    st.session_state.vectorizer = TfidfVectorizer()

def save_chat_history():
    """Save chat history to a JSON file"""
    with open('chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f)

def load_chat_history():
    """Load chat history from JSON file"""
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            st.session_state.chat_history = json.load(f)

def save_course_content(course_name, content):
    """Save course content to a JSON file"""
    with open(f'{course_name}_content.json', 'w') as f:
        json.dump(content, f)

def load_course_content(course_name):
    """Load course content from a JSON file"""
    if os.path.exists(f'{course_name}_content.json'):
        with open(f'{course_name}_content.json', 'r') as f:
            return json.load(f)
    return []

# Sidebar for navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.selectbox(
    "Select Mode",
    ["Course Management", "Student Chat", "Resource Center"]
)

# Course Management
if menu_option == "Course Management":
    st.title("Course Management")
    
    # Add new course content
    with st.expander("Upload Course Content"):
        course_name = st.text_input("Course Name")
        uploaded_file = st.file_uploader("Choose a file", type="txt")
        if st.button("Upload Content") and course_name and uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            st.session_state.course_contents[course_name] = content.splitlines()
            save_course_content(course_name, st.session_state.course_contents[course_name])
            st.success(f"Uploaded content for course: {course_name}")

    # Display existing course contents
    st.subheader("Current Courses and Topics")
    for course, topics in st.session_state.course_contents.items():
        with st.expander(course):
            for topic in topics:
                st.write(f"- {topic}")

# Student Chat
elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")
    
    # Load saved course contents
    selected_course = st.selectbox("Select Course", list(st.session_state.course_contents.keys()))
    content = st.session_state.course_contents.get(selected_course, [])
    
    if content:
        # Process course content using TF-IDF
        tfidf_matrix = st.session_state.vectorizer.fit_transform(content)
    
        # Chat interface
        user_message = st.text_input("Ask your question:")
        if st.button("Send"):
            if user_message:
                # Add user message to chat history
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.chat_history.append({
                    "timestamp": timestamp,
                    "user": user_message,
                    "course": selected_course
                })
                
                # Find the most relevant content
                user_tfidf = st.session_state.vectorizer.transform([user_message])
                similarity_scores = cosine_similarity(user_tfidf, tfidf_matrix).flatten()
                best_match_index = similarity_scores.argmax()
                response = content[best_match_index] if similarity_scores[best_match_index] > 0 else "I'm sorry, I don't have information on that."

                # Display response and save chat history
                st.write(f"Teacher: {response}")
                save_chat_history()

    # Display chat history
    st.subheader("Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.text(f"[{chat['timestamp']}] {chat['course']}")
        st.text(f"Student: {chat['user']}")
        st.text("---")

# Resource Center
else:
    st.title("Resource Center")
    
    # Upload learning materials
    st.subheader("Upload Learning Materials")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
    
    # Resource links
    st.subheader("Useful Links")
    st.markdown("""
    * [Machine Learning Documentation](https://scikit-learn.org/stable/documentation.html)
    * [Deep Learning Resources](https://pytorch.org/tutorials/)
    * [AI Ethics Guidelines](https://www.google.com)
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
