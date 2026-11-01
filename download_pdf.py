import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

conn = snowflake.connector.connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA")
)

cursor = conn.cursor()

# Download the PDF from Snowflake Stage
cursor.execute(
    "GET @DOCUMENT_STAGE/HR_Policy_Document.pdf file://./downloads/"
)

print("✅ PDF downloaded successfully!")

cursor.close()
conn.close()