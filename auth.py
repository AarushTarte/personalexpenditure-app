import bcrypt
from database import conn, cursor

def signup(username, password):
    hashed = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    )

    try:
        cursor.execute(
            """
            INSERT INTO users(username, password)
            VALUES(?, ?)
            """,
            (username, hashed)
        )
        conn.commit()
        return True

    except:
        return False


def login(username, password):
    cursor.execute(
        """
        SELECT password
        FROM users
        WHERE username=?
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user:
        return bcrypt.checkpw(
            password.encode(),
            user[0]
        )

    return False