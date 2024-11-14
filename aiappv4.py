import streamlit as st
from datetime import datetime
import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'courses' not in st.session_state:
    st.session_state.courses = {}
if 'lessons' not in st.session_state:
    st.session_state.lessons = {}

# Helper functions
def save_chat_history():
    """Save chat history to a JSON file for persistence."""
    with open('chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f)

def load_chat_history():
    """Load chat history from JSON file."""
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            st.session_state.chat_history = json.load(f)

def save_lessons():
    """Save lessons to a JSON file for persistence."""
    with open('lessons.json', 'w') as f:
        json.dump(st.session_state.lessons, f)

def load_lessons():
    """Load lessons from JSON file."""
    if os.path.exists('lessons.json'):
        with open('lessons.json', 'r') as f:
            st.session_state.lessons = json.load(f)

def add_lesson(course_name, topic, content):
    """Add new lesson content."""
    if course_name not in st.session_state.lessons:
        st.session_state.lessons[course_name] = {}
    st.session_state.lessons[course_name][topic] = content
    save_lessons()

def find_relevant_content(question, course_name):
    """Find the most relevant content based on question similarity."""
    if course_name not in st.session_state.lessons:
        return "No lesson content available for this course."

    # Gather all lesson content under the selected course
    content_list = []
    topics = []
    for topic, content in st.session_state.lessons[course_name].items():
        content_list.append(content)
        topics.append(topic)
    
    # Convert the lesson contents and the question to TF-IDF embeddings for similarity check
    vectorizer = TfidfVectorizer().fit_transform([question] + content_list)
    cosine_similarities = cosine_similarity(vectorizer[0:1], vectorizer[1:]).flatten()
    most_similar_idx = np.argmax(cosine_similarities)
    
    # Return the most relevant topic and content
    if cosine_similarities[most_similar_idx] > 0.1:  # Threshold for similarity
        return f"**{topics[most_similar_idx]}**: {content_list[most_similar_idx]}"
    else:
        return "No relevant content found for your question."

# Load chat history and lessons on startup
load_chat_history()
load_lessons()

# Sidebar for navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.selectbox(
    "Select Mode",
    ["Course Management", "Student Chat", "Resource Center"]
)

# Main content area
if menu_option == "Course Management":
    st.title("Course Management")

    # Add new course and topics
    new_course = st.text_input("Course Name")
    new_topics = st.text_area("Topics (one per line)")
    if st.button("Add Course"):
        if new_course and new_topics:
            st.session_state.courses[new_course] = new_topics.split('\n')
            st.success(f"Added course: {new_course}")

    # Upload lesson materials for a course
    st.subheader("Upload Lesson Materials")
    selected_course_for_lesson = st.selectbox("Select Course for Lesson Upload", list(st.session_state.courses.keys()))
    lesson_topic = st.text_input("Lesson Topic")
    lesson_content = st.text_area("Lesson Content")
    if st.button("Upload Lesson"):
        add_lesson(selected_course_for_lesson, lesson_topic, lesson_content)
        st.success(f"Lesson '{lesson_topic}' added to course '{selected_course_for_lesson}'")

    # Display current courses and their topics
    st.subheader("Current Courses")
    for course, topics in st.session_state.courses.items():
        with st.expander(course):
            st.write("Topics:")
            for topic in topics:
                st.write(f"- {topic}")
            # Display lesson materials associated with each course
            if course in st.session_state.lessons:
                st.write("Lesson Materials:")
                for topic, content in st.session_state.lessons[course].items():
                    st.write(f"**{topic}**: {content}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")

    # Select course for context
    selected_course = st.selectbox("Select Course", list(st.session_state.courses.keys()))
    
    # Chat interface with content-based answering
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
            
            # Find relevant content from uploaded lessons using similarity
            relevant_content = find_relevant_content(user_message, selected_course)
            
            # Display AI response using relevant content
            st.write("Teacher: " + relevant_content)
            
            save_chat_history()

    # Display chat history
    st.subheader("Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.text(f"[{chat['timestamp']}] {chat['course']}")
        st.text(f"Student: {chat['user']}")
        st.text("---")

else:  # Resource Center
    st.title("Resource Center")
    
    # Upload learning materials
    st.subheader("Upload General Learning Materials")
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
