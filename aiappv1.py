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
# NEW: Add a 'lessons' dictionary to session state to store uploaded lesson files
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

    # NEW: Upload lesson materials for a course
    st.subheader("Upload Lesson Materials")
    selected_course_for_lesson = st.selectbox("Select Course for Lesson Upload", list(st.session_state.courses.keys()))
    lesson_file = st.file_uploader("Choose a file")
    if lesson_file is not None and st.button("Upload Lesson"):
        if selected_course_for_lesson not in st.session_state.lessons:
            st.session_state.lessons[selected_course_for_lesson] = []
        # Store the uploaded lesson in session state
        st.session_state.lessons[selected_course_for_lesson].append({
            "filename": lesson_file.name,
            "content": lesson_file.getvalue()
        })
        st.success(f"Lesson material '{lesson_file.name}' uploaded for {selected_course_for_lesson}!")

    # Display existing courses and their topics
    st.subheader("Current Courses")
    for course, topics in st.session_state.courses.items():
        with st.expander(course):
            st.write("Topics:")
            for topic in topics:
                st.write(f"- {topic}")
            # NEW: Display lesson materials associated with each course
            if course in st.session_state.lessons:
                st.write("Lesson Materials:")
                for lesson in st.session_state.lessons[course]:
                    st.write(f"- {lesson['filename']}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")
    
    # Select course for context
    selected_course = st.selectbox("Select Course", list(st.session_state.courses.keys()))
    
    # NEW: Show available lessons for the selected course in chat
    st.subheader("Available Lessons")
    if selected_course in st.session_state.lessons:
        for lesson in st.session_state.lessons[selected_course]:
            st.write(f"📄 {lesson['filename']}")
            # Download button for each lesson
            st.download_button("Download", lesson['content'], file_name=lesson['filename'])
    else:
        st.write("No lessons available for this course yet.")

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
            
            # Display response (placeholder for actual AI response)
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
