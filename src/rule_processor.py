import os
import PyPDF2

def load_rules(filepath):
    """Reads the rulebook, handling both .txt and .pdf files."""
    if not os.path.exists(filepath):
        return "Rulebook not found."
    
    # Check if the file is a PDF
    if filepath.lower().endswith('.pdf'):
        text = ""
        try:
            with open(filepath, 'rb') as f: # 'rb' means Read Binary
                pdf_reader = PyPDF2.PdfReader(f)
                # Loop through every page and grab the text
                for page in pdf_reader.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
    
    # For normal text file
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

def create_chunks(text, chunk_size=300): # Smaller chunks are better for PDFs
    """Breaks long text into smaller pieces for the AI."""
    if not text:
        return []
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

if __name__ == "__main__":
    # Test with your PDF
    path = "knowledge_base/2026_regs.pdf"
    raw_text = load_rules(path)
    chunks = create_chunks(raw_text)
    
    print(f"Librarian Report:")
    print(f"- File: {path}")
    print(f"- Total Chunks created: {len(chunks)}")
    if chunks:
        print(f"- First 100 characters: {chunks[0][:100]}...")