# =====================================
# app.py PART 1/3
# =====================================

import streamlit as st
import os

from dotenv import load_dotenv
import snowflake.connector

from sentence_transformers import SentenceTransformer
from google import genai

from upload_processor import process_pdf
from snowflake_utils import save_embeddings_to_snowflake
from auth import login_user, logout


# =====================================
# Page Configuration
# =====================================

st.set_page_config(
    page_title="Enterprise RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)


# Load Environment

load_dotenv()



# =====================================
# Snowflake Connection
# =====================================

@st.cache_resource
def connect_snowflake():

    connection = snowflake.connector.connect(

        user=os.getenv("SNOWFLAKE_USER"),

        password=os.getenv("SNOWFLAKE_PASSWORD"),

        account=os.getenv("SNOWFLAKE_ACCOUNT"),

        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),

        database=os.getenv("SNOWFLAKE_DATABASE"),

        schema=os.getenv("SNOWFLAKE_SCHEMA")

    )

    return connection



connection = connect_snowflake()

cursor = connection.cursor()



# =====================================
# Session Login
# =====================================

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False



if "user" not in st.session_state:

    st.session_state.user = None



# =====================================
# Login Page
# =====================================

if not st.session_state.logged_in:


    st.title("🔐 Enterprise RAG Login")


    username = st.text_input(
        "Username"
    )


    password = st.text_input(
        "Password",
        type="password"
    )



    if st.button("Login"):


        user = login_user(

            connection,

            username,

            password

        )


        if user:


            st.session_state.logged_in = True

            st.session_state.user = user


            st.success(
                "Login Successful"
            )


            st.rerun()


        else:


            st.error(
                "Invalid Username or Password"
            )



    st.stop()



# =====================================
# Sidebar User Info
# =====================================

st.sidebar.success(

    f"User: {st.session_state.user['username']}"

)


st.sidebar.info(

    f"Role: {st.session_state.user['role']}"

)



if st.sidebar.button("Logout"):


    logout()

    st.session_state.logged_in = False

    st.session_state.user = None

    st.rerun()



# =====================================
# Load AI Models
# =====================================

@st.cache_resource
def load_models():


    embedding_model = SentenceTransformer(

        "all-MiniLM-L6-v2"

    )


    gemini_client = genai.Client(

        api_key=os.getenv("GEMINI_API_KEY")

    )


    return embedding_model, gemini_client



embedding_model, gemini_client = load_models()


# =====================================
# Admin Dashboard
# =====================================


if st.session_state.user["role"] == "ADMIN":


    with st.sidebar:

        page = st.radio(

            "Navigation",

            [

                "Chat",

                "Admin Dashboard"

            ]

        )


else:

    page = "Chat"



# =====================================
# Admin Dashboard Page
# =====================================

if page == "Admin Dashboard":


    st.title(
        "📊 Admin Dashboard"
    )


    # Total Documents

cursor.execute(
"""
SELECT

FILE_NAME,

DOCUMENT_TYPE,

UPLOADED_BY,

UPLOAD_DATE

FROM DOCUMENT_EMBEDDINGS

ORDER BY UPLOAD_DATE DESC

"""
)


# Total Chunks

cursor.execute(
    """
    SELECT COUNT(*)
    FROM DOCUMENT_EMBEDDINGS
    """
)


result = cursor.fetchone()


if result:

    total_chunks = result[0]

else:

    total_chunks = 0



st.metric(
    "Total Chunks",
    total_chunks
)


    # Total Chunks

cursor.execute(

        """

        SELECT COUNT(*)

        FROM DOCUMENT_EMBEDDINGS

        """

    )


total_chunks = cursor.fetchone()[0]



st.metric(

        "Total Chunks",

        total_chunks

    )



st.subheader(

        "📄 Uploaded Documents"

    )



cursor.execute(

        """

        SELECT DISTINCT

            FILE_NAME,

            DOCUMENT_TYPE,

            UPLOADED_BY,

            UPLOAD_DATE


        FROM DOCUMENT_EMBEDDINGS


        ORDER BY UPLOAD_DATE DESC


        """

    )



documents = cursor.fetchall()



if documents:


        for doc in documents:


            st.write(

                f"""

📄 File : {doc[0]}

📌 Type : {doc[1]}

👤 Uploaded By : {doc[2]}

📅 Date : {doc[3]}

----------------------

"""

            )



        st.subheader(

            "🗑 Delete Document"

        )


        file_list = [

            doc[0]

            for doc in documents

        ]



        delete_file = st.selectbox(

            "Select File",

            file_list

        )



        if st.button(

            "Delete"

        ):



            cursor.execute(

                """

                DELETE FROM DOCUMENT_EMBEDDINGS

                WHERE FILE_NAME=%s


                """,

                (

                    delete_file,

                )

            )


            connection.commit()



            st.success(

                "Document deleted successfully"

            )


            st.rerun()



else:


        st.warning(

            "No documents available"

        )



st.stop()





# =====================================
# Main Chat Page
# =====================================


st.title(

    "🤖 Enterprise RAG Chatbot"

)


st.write(

    "Upload company documents and ask questions using AI"

)





# =====================================
# Chat Memory
# =====================================


if "messages" not in st.session_state:

    st.session_state.messages = []



if st.button(

    "🗑 Clear Chat"

):


    st.session_state.messages = []


    st.success(

        "Chat cleared"

    )





# =====================================
# PDF Upload
# =====================================


st.subheader(

    "📂 Upload Documents"

)



document_type = st.selectbox(

    "Document Type",

    [

        "HR",

        "FINANCE",

        "PUBLIC"

    ]

)



allowed_role = st.selectbox(

    "Allowed Role",

    [

        "ADMIN",

        "HR",

        "EMPLOYEE"

    ]

)



uploaded_files = st.file_uploader(

    "Upload PDF Files",

    type=["pdf"],

    accept_multiple_files=True

)



if uploaded_files:


    uploaded_by = st.session_state.user["username"]



    for uploaded_file in uploaded_files:


        file_path = (

            "documents/"

            +

            uploaded_file.name

        )



        with open(

            file_path,

            "wb"

        ) as f:


            f.write(

                uploaded_file.getbuffer()

            )



        st.success(

            f"{uploaded_file.name} uploaded"

        )



        with st.spinner(

            "Creating embeddings..."

        ):



            chunks, embeddings = process_pdf(

                file_path

            )

            st.write("Number of chunks:", len(chunks))
            st.write("Embedding shape:", len(embeddings))





            save_embeddings_to_snowflake(

                connection,

                uploaded_file.name,

                document_type,

                uploaded_by,

                allowed_role,

                chunks,

                embeddings

            )

            st.success("Embedding function completed")



        st.success(

            f"{len(chunks)} chunks stored successfully"

        )


     # =====================================
# Display Previous Chat Messages
# =====================================


for message in st.session_state.messages:


    with st.chat_message(

        message["role"]

    ):

        st.write(

            message["content"]

        )





# =====================================
# Chat Input
# =====================================


question = st.chat_input(

    "Ask your question..."

)




if question:



    # Save User Message

    st.session_state.messages.append(

        {

            "role": "user",

            "content": question

        }

    )



    with st.chat_message(

        "user"

    ):


        st.write(question)




    # =================================
    # Create Question Embedding
    # =================================


    question_embedding = embedding_model.encode(

        question

    )



    vector_string = (

        "["

        +

        ",".join(

            map(

                str,

                question_embedding.tolist()

            )

        )

        +

        "]"

    )





    # =================================
    # Snowflake Vector Search
    # =================================


sql = """

SELECT

FILE_NAME,

DOCUMENT_TYPE,

CHUNK_ID,

CHUNK_TEXT


FROM DOCUMENT_EMBEDDINGS


WHERE ALLOWED_ROLE IN (%s,'PUBLIC')


ORDER BY

VECTOR_COSINE_SIMILARITY(

EMBEDDING,

PARSE_JSON(%s)::VECTOR(FLOAT,384)

)

DESC


LIMIT 5

"""



user_role = st.session_state.user["role"]



cursor.execute(

        sql,

        (

            user_role,

            "PUBLIC",

            vector_string

        )

    )



results = cursor.fetchall()





    # =================================
    # Prepare Context
    # =================================


context = ""

sources = []



for row in results:



        context += (

            row[3]

            +

            "\n\n"

        )



        sources.append(

            {

                "file": row[0],

                "type": row[1],

                "chunk": row[2]

            }

        )





    # =================================
    # Chat History
    # =================================


history = ""



for msg in st.session_state.messages:



        history += (

            msg["role"]

            +

            ": "

            +

            msg["content"]

            +

            "\n"

        )





    # =================================
    # Gemini Prompt
    # =================================


prompt = f"""

You are an Enterprise RAG Assistant.


Answer only using the document context.


If information is not available,
say:

"Information not found in documents."



Document Context:

{context}



Conversation History:

{history}



Question:

{question}


"""





response = gemini_client.models.generate_content(


        model="gemini-2.5-flash",


        contents=prompt


    )



answer = response.text





    # =================================
    # Save Assistant Message
    # =================================


st.session_state.messages.append(

        {

            "role": "assistant",

            "content": answer

        }

    )





    # =================================
    # Display Answer
    # =================================


with st.chat_message(

        "assistant"

    ):



        st.write(

            answer

        )



        st.subheader(

            "📄 Sources"

        )



        for source in sources:



            st.write(

                f"""

📄 File: {source['file']}

📌 Type: {source['type']}

🔹 Chunk: {source['chunk']}

"""

            )   