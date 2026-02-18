import os
import PyPDF2
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM

def load_rules(filepath):
    """Same as yesterday: Reads the PDF/Text."""
    if not os.path.exists(filepath): return ""
    if filepath.endswith('.pdf'):
        text = ""
        with open(filepath, 'rb') as f:
            pdf = PyPDF2.PdfReader(f)
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    else:
        with open(filepath, 'r') as f: return f.read()

def create_chunks(text, chunk_size=500):
    """Breaks text into pieces so the AI doesn't get overwhelmed."""
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def get_vector_db(chunks):
    """The 'Aisle Mapper': Turns text into searchable math coordinates."""
    # This model 'all-MiniLM-L6-v2' is FREE
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = FAISS.from_texts(chunks, embeddings)
    return vector_db

def ask_ai(query, vector_db):
    """The 'Expert': Finds the rule and explains it."""
    # 1. Find the top 2 most relevant paragraphs
    docs = vector_db.similarity_search(query, k=2)
    context = "\n".join([d.page_content for d in docs])
    
    # 2. Ask our local Llama 3 brain to explain it
    llm = OllamaLLM(model="llama3.2:1b")
    
    prompt = f"""
    You are an F1 Technical Engineer. Use the following rulebook snippets to answer the user.
    If the answer isn't in the snippets, say you don't know.
    
    Rules: {context}
    Question: {query}
    Answer:"""
    
    return llm.invoke(prompt)