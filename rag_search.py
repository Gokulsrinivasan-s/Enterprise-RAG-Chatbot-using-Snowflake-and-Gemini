import os
from dotenv import load_dotenv
import snowflake.connector

from sentence_transformers import SentenceTransformer


# Load environment
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


# Load embedding model

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# User Question

question = input(
    "Ask your question: "
)


# Convert question to vector

question_embedding = model.encode(
    question
)


print("Question converted into vector")


# Convert vector to string

vector_string = "[" + ",".join(
    map(str, question_embedding.tolist())
) + "]"


# Search similar chunks

sql = """
SELECT
    CHUNK_TEXT
FROM DOCUMENT_EMBEDDINGS
ORDER BY
    VECTOR_COSINE_SIMILARITY(
        EMBEDDING,
        PARSE_JSON(%s)::VECTOR(FLOAT,384)
    ) DESC
LIMIT 1
"""


cursor.execute(
    sql,
    (vector_string,)
)


result = cursor.fetchone()


print("\nMost Relevant Information:")
print("--------------------------------")
print(result[0])


cursor.close()
connection.close()