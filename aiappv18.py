import subprocess
import streamlit as st
from datetime import datetime
import json
import os
import openai

# Check if openai library is installed, if not, install it
try:
    import openai
except ImportError:
    subprocess.check_call(["pip", "install", "openai"])
    import openai

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

# Initialize OpenAI API key
openai.api_key = st.secrets["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"]

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
            
            # Generate AI response using OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Answer the following question based on the course '{selected_course}': {user_message}",
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0.5
            )
            ai_response = response.choices[0].text.strip()
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                "timestamp": timestamp,
                "teacher": ai_response,
                "course": selected_course
            })
            
            # Display AI response
            st.write("Teacher: " + ai_response)
            save_chat_history()

    # Display chat history
    st.subheader("Chat History")
    for chat in reversed(st.session_state.chat_history):
        st.text(f"[{chat['timestamp']}] {chat['course']}")
        if 'user' in chat:
            st.text(f"Student: {chat['user']}")
        elif 'teacher' in chat:
            st.text(f"Teacher: {chat['teacher']}")
        st.text("---")

else:  # Resource Center
    st.title("Resource Center")
    
    # Upload learning materials
    st.subheader("Upload Learning Materials")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # Save uploaded file to a directory
        with open(os.path.join("learning_materials", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getvalue())
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
