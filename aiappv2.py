import streamlit as st
from datetime import datetime
import json
import os

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
    """Save chat history to a JSON file"""
    with open('chat_history.json', 'w') as f:
        json.dump(st.session_state.chat_history, f)

def load_chat_history():
    """Load chat history from JSON file"""
    if os.path.exists('chat_history.json'):
        with open('chat_history.json', 'r') as f:
            st.session_state.chat_history = json.load(f)

# Function to suggest lessons based on keywords
def suggest_lessons(course, question):
    suggestions = []
    for topic, lesson_files in st.session_state.lessons.get(course, {}).items():
        if topic.lower() in question.lower():  # Basic keyword matching
            suggestions.append((topic, lesson_files))
    return suggestions

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

    # Upload lesson materials for a course
    st.subheader("Upload Lesson Materials")
    selected_course_for_lesson = st.selectbox("Select Course for Lesson Upload", list(st.session_state.courses.keys()))
    lesson_topic = st.text_input("Lesson Topic")
    lesson_file = st.file_uploader("Choose a file")
    if lesson_file is not None and st.button("Upload Lesson"):
        # Initialize lessons for the course if not already
        if selected_course_for_lesson not in st.session_state.lessons:
            st.session_state.lessons[selected_course_for_lesson] = {}
        # Store lesson file under the topic
        st.session_state.lessons[selected_course_for_lesson].setdefault(lesson_topic, []).append({
            "filename": lesson_file.name,
            "content": lesson_file.getvalue()
        })
        st.success(f"Lesson material '{lesson_file.name}' uploaded under topic '{lesson_topic}'!")

    # Display existing courses and their topics
    st.subheader("Current Courses")
    for course, topics in st.session_state.courses.items():
        with st.expander(course):
            st.write("Topics:")
            for topic in topics:
                st.write(f"- {topic}")
            # Display lesson materials associated with each course
            if course in st.session_state.lessons:
                st.write("Lesson Materials:")
                for topic, lessons in st.session_state.lessons[course].items():
                    st.write(f"**{topic}**:")
                    for lesson in lessons:
                        st.write(f"- {lesson['filename']}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")
    
    # Select course for context
    selected_course = st.selectbox("Select Course", list(st.session_state.courses.keys()))
    
    # Show available lessons for the selected course
    st.subheader("Available Lessons")
    if selected_course in st.session_state.lessons:
        for topic, lessons in st.session_state.lessons[selected_course].items():
            st.write(f"**{topic}**:")
            for lesson in lessons:
                st.write(f"- {lesson['filename']}")
                st.download_button("Download", lesson['content'], file_name=lesson['filename'])
    else:
        st.write("No lessons available for this course yet.")

    # Chat interface with lesson suggestion
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
            
            # Suggest relevant lessons
            suggestions = suggest_lessons(selected_course, user_message)
            if suggestions:
                st.write("Teacher: Based on your question, you might find these resources helpful:")
                for topic, lesson_files in suggestions:
                    st.write(f"**Topic: {topic}**")
                    for lesson in lesson_files:
                        st.write(f"- {lesson['filename']}")
                        st.download_button("Download", lesson['content'], file_name=lesson['filename'])
            else:
                st.write("Teacher: Thank you for your question about " + selected_course + 
                        ". I'll help you understand this topic better.")
            
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
