import os
import PyPDF2
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import streamlit as st

groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

def load_rules(folder_path):
    combined_text = ""
    if not os.path.exists(folder_path): return "Folder not found."
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            with open(filepath, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                for page in pdf.pages: combined_text += page.extract_text() + "\n"
        elif filename.endswith('.txt'):
            with open(filepath, 'r') as f: combined_text += f.read() + "\n"
    return combined_text

def create_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_text(text)

def get_vector_db(chunks):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_texts(chunks, embeddings)

def ask_ai(query, vector_db):
    docs = vector_db.similarity_search(query, k=3)
    context = "\n".join([d.page_content for d in docs])
    
    # Using Llama 3 on Groq for professional speed
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0,groq_api_key=groq_api_key)
    
    prompt = f"System: You are an F1 Race Engineer. Use the rules below to answer.\nRules: {context}\nUser: {query}"
    return llm.invoke(prompt).content