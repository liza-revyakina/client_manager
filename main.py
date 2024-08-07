import psycopg2
from config import PASSWORD


def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
                CREATE TABLE IF NOT EXISTS client(
                    id SERIAL PRIMARY KEY,
                    firstname VARCHAR(40) NOT NULL,
                    lastname VARCHAR(40) NOT NULL,
                    email VARCHAR(40) NOT NULL
                );
                """)
        cur.execute("""
                CREATE TABLE IF NOT EXISTS phone_number(
                    id SERIAL PRIMARY KEY,
                    number VARCHAR(64),
                    client_id INTEGER NOT NULL REFERENCES client(id) ON DELETE CASCADE
                );
                """)
        conn.commit()
    pass


def add_client(conn, firstname, lastname, email, number=None):
    with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO client(firstname, lastname, email) 
                VALUES(%s, %s, %s) RETURNING id;
                """, (firstname, lastname, email))
        conn.commit()
        client_id = int(cur.fetchone()[0])
        if number is not None:
            cur.execute("""
                    INSERT INTO phone_number(number, client_id) 
                    VALUES(%s, %s) RETURNING id;
                    """, (number, client_id))
            conn.commit()
            print(f'Client id: {client_id}\nNumber id: {int(cur.fetchone()[0])}\n')
            return client_id
        elif number is None:
            print(f'Client id: {client_id}\n')
            return client_id
    pass


def add_phone(conn, number, client_id):
    with conn.cursor() as cur:
        cur.execute("""
                INSERT INTO phone_number(number, client_id) 
                VALUES(%s, %s) RETURNING id;
                """, (number, client_id))
        conn.commit()
        number_id = int(cur.fetchone()[0])
        print(f'Client id: {client_id}\nNumber id: {number_id}\n')
        return number_id
    pass


def change_client(conn, client_id, firstname=None, lastname=None, email=None, number=None):
    with conn.cursor() as cur:
        columns = ['firstname', 'lastname', 'email', 'number']
        arguments = [firstname, lastname, email, number]
        for idx, each in enumerate(arguments):
            result = columns[idx]
            if each is not None:
                if each != number:
                    cur.execute(f"""
                            UPDATE client SET {result} = %s
                            WHERE id = %s;
                            """, (each, client_id))
                    conn.commit()
                elif each == number:
                    cur.execute(f"""
                            UPDATE phone_number SET {result} = %s
                            WHERE id = %s;
                            """, (each, client_id))
                    conn.commit()
        print('Data changed successfully')
    pass


def delete_phone(conn, client_id, number):
    with conn.cursor() as cur:
        cur.execute("""
        DELETE FROM phone_number
        WHERE client_id = %s AND number = %s;
        """, (client_id, number))
        print('Number deleted successfully')
    pass


def delete_client(conn, pk):
    with conn.cursor() as cur:
        cur.execute("""
                DELETE FROM client
                WHERE id = %s;
                """, (pk,))
        conn.commit()
        print('Client deleted successfully')
    pass


def find_client(conn, firstname=None, lastname=None, email=None, number=None):
    with conn.cursor() as cur:
        cur.execute('''
            SELECT * FROM client c
            LEFT JOIN phone_number p ON c.id = p.client_id
            WHERE
            (firstname = %(firstname)s OR %(firstname)s IS NULL) AND
            (lastname = %(lastname)s OR %(lastname)s IS NULL) AND
            (email = %(email)s OR %(email)s IS NULL) AND
            (number = %(number)s OR %(number)s IS NULL)
        ''', locals())
        return cur.fetchall()
    pass


with psycopg2.connect(database="client_manager", user="postgres", password=PASSWORD) as conn:
    pass  # вызывайте функции здесь
    create_db(conn)
    new_client_id = add_client(conn, 'Robert', 'Walker', 'rbrtwlkr@mail.com', 11111111)
    new_number_id = add_phone(conn, 22222222, 1)
    change_client(conn, 1, lastname='Polson')
    print(find_client(conn, lastname='Polson', number='11111111'))
    delete_phone(conn, 1, '11111111')
    delete_client(conn, 1)

conn.close()
