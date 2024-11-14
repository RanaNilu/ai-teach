import streamlit as st
from datetime import datetime
import json
import os
import re

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

def save_chat_history():
    """Save chat history to a JSON file"""
    with open('chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f)

def load_chat_history():
    """Load chat history from JSON file"""
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            st.session_state.chat_history = json.load(f)

def process_question(question, lessons):
    """Process the question and return a relevant response based on uploaded lessons."""
    question = question.lower()
    for title, content in lessons.items():
        content_lower = content.lower()
        if re.search(r'\b' + re.escape(question) + r'\b', content_lower):
            return f"Based on the lesson '{title}', here's some information: {content}"
    return "I'm sorry, but I couldn't find an answer based on the uploaded lessons."

# Sidebar for navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.selectbox(
    "Select Mode",
    ["Course Management", "Student Chat", "Resource Center"]
)

# Main content area
if menu_option == "Course Management":
    st.title("Course Management")
    
    # Add new course
    with st.expander("Add New Course"):
        new_course = st.text_input("Course Name")
        new_topics = st.text_area("Topics (one per line)")
        if st.button("Add Course"):
            if new_course and new_topics:
                st.session_state.courses[new_course] = new_topics.split('\n')
                st.success(f"Added course: {new_course}")

    # Display existing courses
    st.subheader("Current Courses")
    for course, topics in st.session_state.courses.items():
        with st.expander(course):
            st.write("Topics:")
            for topic in topics:
                st.write(f"- {topic}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")
    
    # Select course for context
    selected_course = st.selectbox("Select Course", list(st.session_state.courses.keys()))
    
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
            
            # Generate response based on uploaded lessons
            response = process_question(user_message, st.session_state.lessons)
            st.write(response)
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
    st.subheader("Upload Learning Materials")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        lesson_content = uploaded_file.read().decode("utf-8")
        lesson_title = uploaded_file.name
        st.session_state.lessons[lesson_title] = lesson_content
        st.success(f"File '{lesson_title}' uploaded successfully!")

    # Display uploaded lessons
    st.subheader("Uploaded Lessons")
    for title, content in st.session_state.lessons.items():
        with st.expander(title):
            st.write(content)

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