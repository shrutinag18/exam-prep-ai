from pypdf import PdfReader
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pptx import Presentation

def load_pdf(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def load_docx(file):
    doc = Document(file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


def load_document(file):

    if file.name.endswith(".pdf"):
        return load_pdf(file)

    elif file.name.endswith(".docx"):
        return load_docx(file)
    
    elif file.name.endswith(".pptx"):
        return load_pptx(file)

    else:
        raise ValueError(f"Unsupported file format: {file.name}")

def split_text(text, chunk_size=500, chunk_overlap=50):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_text(text)

    print(f"Split into {len(chunks)} chunks")

    return chunks
def load_pptx(file):

    presentation = Presentation(file)

    text = ""

    for slide in presentation.slides:

        for shape in slide.shapes:

            if hasattr(shape, "text"):

                text += shape.text + "\n"

    return text