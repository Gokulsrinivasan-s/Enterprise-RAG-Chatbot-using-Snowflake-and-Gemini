import streamlit as st


def login_user(connection, username, password):

    cursor = connection.cursor()


    sql = """
    SELECT 
        USERNAME,
        ROLE

    FROM USERS

    WHERE USERNAME=%s
    AND PASSWORD=%s
    """


    cursor.execute(
        sql,
        (
            username,
            password
        )
    )


    result = cursor.fetchone()


    cursor.close()


    if result:

        return {
            "username": result[0],
            "role": result[1]
        }


    return None



def logout():

    st.session_state.logged_in = False
    st.session_state.user = None