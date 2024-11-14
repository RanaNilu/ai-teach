import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
import json
import os

# File paths for storing persistent data
COURSE_CONTENT_FILE = "course_content.json"
CHAT_HISTORY_FILE = "chat_history.json"

# Configure Streamlit app
st.set_page_config(
    page_title="AI Teaching Assistant",
    page_icon="🎓",
    layout="wide"
)

# Helper Functions
def load_json(file_path):
    """Load JSON data from a file."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return {}

def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def parse_uploaded_content(file_content):
    """Parse uploaded content into a list of topics."""
    content = file_content.decode("utf-8")
    return [line.strip() for line in content.splitlines() if line.strip()]

def find_most_relevant_answer(question, course_content):
    """Find the most relevant answer using TF-IDF and cosine similarity."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([question] + course_content)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    best_match_idx = cosine_similarities.argmax()
    if cosine_similarities[best_match_idx] > 0:
        return course_content[best_match_idx]
    return "Sorry, I couldn't find a match. Please rephrase your question."

# Load persistent data
st.session_state.uploaded_content = load_json(COURSE_CONTENT_FILE)
st.session_state.chat_history = load_json(CHAT_HISTORY_FILE)

# Sidebar Navigation
st.sidebar.title("AI Teaching Assistant")
menu_option = st.sidebar.radio("Navigation", ["Course Management", "Student Chat", "Resource Center"])

# Main Content
if menu_option == "Course Management":
    st.title("Course Management")

    # Upload new course
    st.subheader("Upload New Course")
    uploaded_file = st.file_uploader("Upload a TXT file with course content (one topic per line)", type="txt")
    if uploaded_file:
        course_name = st.text_input("Enter Course Name:")
        if course_name and st.button("Save Course"):
            topics = parse_uploaded_content(uploaded_file.read())
            st.session_state.uploaded_content[course_name] = topics
            save_json(st.session_state.uploaded_content, COURSE_CONTENT_FILE)
            st.success(f"Course '{course_name}' has been uploaded successfully!")

    # Display existing courses
    st.subheader("Existing Courses")
    for course, topics in st.session_state.uploaded_content.items():
        with st.expander(course):
            for topic in topics:
                st.write(f"- {topic}")

elif menu_option == "Student Chat":
    st.title("Chat with AI Teacher")

    # Course Selection
    selected_course = st.selectbox("Select Course", list(st.session_state.uploaded_content.keys()))
    
    if selected_course:
        # Chat Interface
        user_message = st.text_input("Ask a question:")
        if st.button("Send"):
            course_content = st.session_state.uploaded_content[selected_course]
            response = find_most_relevant_answer(user_message, course_content)
            
            # Save chat history
            chat_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "course": selected_course,
                "user": user_message,
                "response": response
            }
            st.session_state.chat_history.append(chat_entry)
            save_json(st.session_state.chat_history, CHAT_HISTORY_FILE)

            # Display response
            st.write(f"Teacher: {response}")

        # Display Chat History
        st.subheader("Chat History")
        for chat in reversed(st.session_state.chat_history):
            if chat["course"] == selected_course:
                st.text(f"[{chat['timestamp']}]")
                st.text(f"Student: {chat['user']}")
                st.text(f"Teacher: {chat['response']}")
                st.text("---")

else:  # Resource Center
    st.title("Resource Center")

    st.subheader("Useful Links")
    st.markdown("""
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Scikit-Learn Documentation](https://scikit-learn.org/stable/documentation.html)
    - [Python Official Docs](https://www.python.org/doc/)
    """)

    st.subheader("Upload Learning Materials")
    st.markdown("Coming Soon!")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and Machine Learning")
