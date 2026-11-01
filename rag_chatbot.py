import os
from dotenv import load_dotenv
import snowflake.connector
from sentence_transformers import SentenceTransformer
from google import genai

# -----------------------------------
# Load Environment Variables
# -----------------------------------

load_dotenv()

# -----------------------------------
# Connect to Snowflake
# -----------------------------------

connection = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

cursor = connection.cursor()

print("✅ Connected to Snowflake")

# -----------------------------------
# Gemini Client
# -----------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("✅ Gemini Connected")

# -----------------------------------
# Load Embedding Model
# -----------------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

print("✅ Embedding Model Loaded")

# -----------------------------------
# User Question
# -----------------------------------

question = input("\nAsk your question: ")

# -----------------------------------
# Create Question Embedding
# -----------------------------------

question_embedding = model.encode(question)

vector_string = "[" + ",".join(
    map(str, question_embedding.tolist())
) + "]"

print("✅ Question converted into embedding")

# -----------------------------------
# Search Top 3 Chunks
# -----------------------------------

sql = """
SELECT
    CHUNK_TEXT
FROM DOCUMENT_EMBEDDINGS
ORDER BY
VECTOR_COSINE_SIMILARITY(
    EMBEDDING,
    PARSE_JSON(%s)::VECTOR(FLOAT,384)
)
DESC
LIMIT 3
"""

cursor.execute(sql, (vector_string,))

rows = cursor.fetchall()

# -----------------------------------
# Combine Context
# -----------------------------------

context = ""

for row in rows:
    context += row[0]
    context += "\n\n"

print("\nRetrieved Context:\n")
print(context)

# -----------------------------------
# Gemini Prompt
# -----------------------------------

prompt = f"""
You are an Enterprise HR Assistant.

Answer ONLY from the context below.

If the answer is not present in the context,
reply:

'I couldn't find that information in the uploaded documents.'

Context:

{context}

Question:

{question}
"""

# -----------------------------------
# Gemini Response
# -----------------------------------

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print("\n" + "=" * 60)
print("AI Answer")
print("=" * 60)
print(response.text)

# -----------------------------------
# Close Connection
# -----------------------------------

cursor.close()
connection.close()

print("\n✅ Connection Closed")