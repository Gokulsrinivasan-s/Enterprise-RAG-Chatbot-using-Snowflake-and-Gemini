# =====================================
# snowflake_utils.py
# =====================================

import snowflake.connector


def save_embeddings_to_snowflake(
        connection,
        file_name,
        document_type,
        uploaded_by,
        allowed_role,
        chunks,
        embeddings
):


    print("SAVE FUNCTION STARTED")

    cursor = connection.cursor()


    print("Chunks received:", len(chunks))


    for i, vector in enumerate(embeddings):


        sql = """

        INSERT INTO DOCUMENT_EMBEDDINGS
        (
            FILE_NAME,
            DOCUMENT_TYPE,
            UPLOADED_BY,
            ALLOWED_ROLE,
            CHUNK_ID,
            CHUNK_TEXT,
            EMBEDDING
        )

        SELECT

            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            PARSE_JSON(%s)::VECTOR(FLOAT,384)

        """


        vector_string = "[" + ",".join(
            map(str, vector.tolist())
        ) + "]"



        cursor.execute(
            sql,
            (
                file_name,
                document_type,
                uploaded_by,
                allowed_role,
                i,
                chunks[i],
                vector_string
            )
        )


    connection.commit()


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM DOCUMENT_EMBEDDINGS
        """
    )


    count = cursor.fetchone()


    print(
        "Snowflake rows:",
        count[0]
    )


    cursor.close()
