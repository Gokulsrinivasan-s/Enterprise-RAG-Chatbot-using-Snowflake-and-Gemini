import os
from dotenv import load_dotenv
import snowflake.connector

from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


# Load .env
load_dotenv()


# Connect Snowflake
connection = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

cursor = connection.cursor()

print("Connected to Snowflake")


# -----------------------------
# 1. Read PDF
# -----------------------------

reader = PdfReader(
    "downloads/HR_Policy_Document.pdf"
)

text = ""

for page in reader.pages:
    text += page.extract_text()


# -----------------------------
# 2. Create Chunks
# -----------------------------

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_text(text)

print("Total chunks:", len(chunks))


# -----------------------------
# 3. Load Embedding Model
# -----------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# Create vectors

embeddings = model.encode(chunks)


print("Embeddings created")


# -----------------------------
# 4. Insert into Snowflake
# -----------------------------

for i, vector in enumerate(embeddings):

    chunk_text = chunks[i]

    vector_string = "[" + ",".join(
        map(str, vector.tolist())
    ) + "]"


    sql = """
    INSERT INTO DOCUMENT_EMBEDDINGS
    (
        FILE_NAME,
        CHUNK_TEXT,
        EMBEDDING
    )
    SELECT
        %s,
        %s,
        PARSE_JSON(%s)::VECTOR(FLOAT,384)
    """


    cursor.execute(
        sql,
        (
            "HR_Policy_Document.pdf",
            chunk_text,
            vector_string
        )
    )


print("Embeddings inserted successfully!")
