import streamlit as st
from datetime import datetime
import json
import os
from pathlib import Path

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
    st.session_state.courses = {
        "Machine Learning Basics": [
            "Introduction to ML",
            "Supervised Learning",
            "Unsupervised Learning",
            "Neural Networks"
        ],
        "Deep Learning": [
            "CNN",
            "RNN",
            "Transformers",
            "GANs"
        ]
    }
if 'lessons' not in st.session_state:
    st.session_state.lessons = {}

def save_chat_history():
    with open('chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f)

def load_chat_history():
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            st.session_state.chat_history = json.load(f)

def save_lessons():
    with open('lessons.json', 'w') as f:
        json.dump(st.session_state.lessons, f)

def load_lessons():
    if os.path.exists('lessons.json'):
        with open('lessons.json', 'r') as f:
            st.session_state.lessons = json.load(f)

# Sidebar for navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.selectbox(
    "Select Mode",
    ["Course Management", "Student Chat", "Lesson Upload", "Resource Center"]
)

# Main content area
if menu_option == "Course Management":
    st.title("Course Management")
    
    with st.expander("Add New Course"):
        new_course = st.text_input("Course Name")
        new_topics = st.text_area("Topics (one per line)")
        if st.button("Add Course"):
            if new_course and new_topics:
                st.session_state.courses[new_course.lower()] = [topic.lower() for topic in new_topics.split('\n')]
                st.success(f"Added course: {new_course}")

    st.subheader("Current Courses")
    for course, topics in st.session_state.courses.items():
        with st.expander(course.title()):
            st.write("Topics:")
            for topic in topics:
                st.write(f"- {topic.title()}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")

    selected_course = st.selectbox("Select Course", [course.title() for course in st.session_state.courses])
    selected_course_key = next((key for key, value in st.session_state.courses.items() if value.title() == selected_course), None)

    user_message = st.text_input("Ask your question:")
    if st.button("Send"):
        if user_message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_history.append({
                "timestamp": timestamp,
                "user": user_message.lower(),
                "course": selected_course_key.lower()
            })

            # Search through lesson content for relevant information
            relevant_lessons = [lesson for lesson in st.session_state.lessons.get(selected_course_key.lower(), []) if user_message.lower() in lesson.lower()]
            if relevant_lessons:
                response = f"Based on your question, here are some relevant lesson topics:\n{'- '.join(relevant_lessons)}"
            else:
                response = f"Thank you for your question about {selected_course}. I'll do my best to provide a helpful response."
            st.write("Teacher: " + response)
            save_chat_history()

    st.subheader("Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.text(f"[{chat['timestamp']}] {chat['course'].title()}")
        st.text(f"Student: {chat['user'].title()}")
        st.text("---")

elif menu_option == "Lesson Upload":
    st.title("Upload Lessons")

    selected_course = st.selectbox("Select Course", [course.title() for course in st.session_state.courses])
    selected_course_key = next((key for key, value in st.session_state.courses.items() if value.title() == selected_course), None)

    uploaded_file = st.file_uploader("Choose a lesson file")
    if uploaded_file is not None:
        lesson_content = uploaded_file.getvalue().decode("utf-8").lower()
        lesson_topics = [topic.strip() for topic in lesson_content.split('\n') if topic.strip()]
        st.session_state.lessons.setdefault(selected_course_key.lower(), []).extend(lesson_topics)
        st.success(f"Lesson uploaded for {selected_course}")
        save_lessons()

    st.subheader("Uploaded Lessons")
    for course, lessons in st.session_state.lessons.items():
        with st.expander(st.session_state.courses[course].title()):
            for lesson in lessons:
                st.write(f"- {lesson.title()}")

else:  # Resource Center
    st.title("Resource Center")
    
    st.subheader("Upload Learning Materials")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        st.success("File uploaded successfully!")
    
    st.subheader("Useful Links")
    st.markdown("""
    * [Machine Learning Documentation](https://scikit-learn.org/stable/documentation.html)
    * [Deep Learning Resources](https://pytorch.org/tutorials/)
    * [AI Ethics Guidelines](https://www.google.com)
    """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")