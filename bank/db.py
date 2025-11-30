import sqlite3

DB_NAME = "bank_db"
DB_FILE = DB_NAME + ".db"
TABLE_NAME = "Tuition"


def _init_db():
    with sqlite3.connect(DB_FILE) as conn:
        query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} (id int PRIMARY KEY, total_tuition REAL, balance REAL)"

        conn.execute(query)


_init_db()


def get_tuition(id):
    with sqlite3.connect(DB_FILE) as conn:
        # conn.row_factory = sqlite3.Row # to return as dict

        query = f"SELECT total_tuition, balance FROM {TABLE_NAME} WHERE id = ?"
        cur = conn.execute(query, (id,))

        result = cur.fetchone()
        if result == None:
            raise FileNotFoundError(f"student not found: {id}")

        return result  # (total_tuition, balance)


def _update_tuition_and_balance(id, tuition, balance):
    with sqlite3.connect(DB_FILE) as conn:
        query = f"UPDATE {TABLE_NAME} SET total_tuition = ?, balance = ? WHERE id = ?"

        conn.execute(query, (tuition, balance, id))


def add_tuition_and_balance(id, tuition, balance):
    with sqlite3.connect(DB_FILE) as conn:
        q = f"SELECT * FROM {TABLE_NAME} WHERE id = ?"
        cur = conn.execute(q, (id,))

        if cur.fetchone() == None:  # add student if student wasn't in the table before
            q = f"INSERT INTO {TABLE_NAME} (id) VALUES (?)"
            conn.execute(q, (id,))

    _update_tuition_and_balance(id, tuition, balance)


if __name__ == "__main__":
    add_tuition_and_balance(22070006038, 2, 100)
    print("added tuition or updated")
    print(get_tuition(22070006038))
