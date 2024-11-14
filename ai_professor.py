import streamlit as st
from langchain.schema import AIMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from PyPDF2 import PdfReader
import hashlib
from streamlit_pdf_viewer import pdf_viewer
import tempfile
import os

# API Keys
google_api_key = st.secrets["google_api_key"]
openai_api_key = st.secrets["openai_api_key"]

st.set_page_config(page_title="AI Professor", page_icon="👨‍🏫")
st.title("👨‍🏫 AI Professor")

# Helper Functions
def get_pdf_text(pdf_docs):
    """Extract text from PDF documents."""
    text = ""
    if isinstance(pdf_docs, list):
        for pdf in pdf_docs:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                text += page.extract_text()
    else:
        pdf_reader = PdfReader(pdf_docs)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    """Split text into manageable chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    """Create a FAISS vector store from text chunks."""
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    return vector_store

def get_response(user_query, chat_history, vector_store):
    """Generate a response using LangChain."""
    template = """
    You are a helpful assistant. Use the provided context and chat history to answer the user's question.

    Context: {context}
    Chat history: {chat_history}
    User question: {user_question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatOpenAI(openai_api_key=openai_api_key, model="gpt-4", temperature=0.7)
    docs = vector_store.similarity_search(user_query, k=5)
    context = "\n".join([doc.page_content for doc in docs])

    response = llm.predict(prompt.format(context=context, chat_history=chat_history, user_question=user_query))
    return response

def get_pdf_hash(pdf_docs):
    """Generate a hash for the uploaded PDFs."""
    combined_hash = hashlib.md5()
    content = pdf_docs.read()
    combined_hash.update(content)
    pdf_docs.seek(0)  # Reset the stream position
    return combined_hash.hexdigest()

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content="Hello! I am your AI assistant. How can I help you?")]
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "current_pdf_hash" not in st.session_state:
    st.session_state.current_pdf_hash = None

# Display Chat History
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# Sidebar for PDF Upload
with st.sidebar:
    st.title("Menu:")
    uploaded_pdf = st.file_uploader("Upload PDF Course Material", type=["pdf"])
    if uploaded_pdf:
        view_pdf = st.checkbox("View PDF")
        if view_pdf:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(uploaded_pdf.read())
                temp_pdf_path = temp_file.name
            pdf_viewer(temp_pdf_path, width=800)

# Process PDF and Generate Vector Store
if uploaded_pdf:
    new_hash = get_pdf_hash(uploaded_pdf)
    if new_hash != st.session_state.current_pdf_hash:
        pdf_text = get_pdf_text(uploaded_pdf)
        text_chunks = get_text_chunks(pdf_text)
        st.session_state.vector_store = get_vector_store(text_chunks)
        st.session_state.current_pdf_hash = new_hash
        st.success("PDF processed successfully!")

# Chat Input
user_query = st.chat_input("Ask your question here...")
if user_query:
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.write(user_query)

    if st.session_state.vector_store:
        with st.chat_message("AI"):
            with st.spinner("Thinking..."):
                response = get_response(user_query, st.session_state.chat_history, st.session_state.vector_store)
                st.write(response)
                st.session_state.chat_history.append(AIMessage(content=response))
    else:
        st.error("Please upload a PDF first!")
