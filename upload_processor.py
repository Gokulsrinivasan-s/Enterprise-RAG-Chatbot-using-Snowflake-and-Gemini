from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def process_pdf(file_path):

    # Read PDF

    reader = PdfReader(file_path)

    text = ""


    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text



    # Create chunks

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )


    chunks = splitter.split_text(text)



    # Create embeddings

    embeddings = model.encode(
        chunks
    )


    print(
        "Total chunks:",
        len(chunks)
    )


    print(
        "Embeddings created"
    )


    return chunks, embeddings