import psycopg2
from config import PASSWORD


with psycopg2.connect(database="client_manager", user="postgres", password=PASSWORD) as conn:
    with conn.cursor() as cur:
        def create_table():
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

        def insert_client(firstname, lastname, email, number=None):
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

        def insert_number(number, client_id):
            cur.execute("""
                    INSERT INTO phone_number(number, client_id) 
                    VALUES(%s, %s) RETURNING id;
                    """, (number, client_id))
            conn.commit()
            number_id = int(cur.fetchone()[0])
            print(f'Client id: {client_id}\nNumber id: {number_id}\n')
            return number_id

        def update_data(column, data, pk):
            if column != 'number':
                cur.execute(f"""
                        UPDATE client SET {column} = %s
                        WHERE id = %s;
                        """, (data, pk))
                conn.commit()
                print('Data changed successfully')
            elif column == 'number':
                cur.execute("""
                        UPDATE phone_number SET number = %s
                        WHERE id = %s;
                        """, (data, pk))
                conn.commit()
                print('Number changed successfully')

        def delete_number(pk=None, client_id=None):
            if pk is not None:
                cur.execute("""
                        DELETE FROM phone_number
                        WHERE id = %s;
                        """, (pk, ))
                conn.commit()
                print('Number deleted successfully')
            elif client_id is not None:
                cur.execute("""
                        DELETE FROM phone_number
                        WHERE client_id = %s;
                        """, (client_id, ))
                conn.commit()
                print('All phone numbers of the client deleted successfully')
            else:
                print('Please, enter number id or client id and try again')

        def delete_client(pk):
            cur.execute("""
                    DELETE FROM client
                    WHERE id = %s;
                    """, (pk,))
            conn.commit()
            print('Client deleted successfully')

        def search_client(firstname=None, lastname=None, email=None, number=None):
            arguments = ['firstname', 'lastname', 'email', 'number']
            for idx, each in enumerate([firstname, lastname, email, number]):
                result = arguments[idx].replace("'", "")
                if each is not None:
                    cur.execute(f"""
                            SELECT * FROM client c
                            LEFT JOIN phone_number p ON c.id = p.client_id
                            WHERE {result} = %s;
                            """, (each,))
                    conn.commit()
                    print(cur.fetchone())


        new_client_id = insert_client('Robert', 'Walker', 'rbrtwlkr@mail.com', 11111111)
        print(new_client_id)

        new_number_id = insert_number(22222222, 1)
        print(new_number_id)

        update_data('number', '11111111', 1)
        update_data('lastname', 'Polson', 1)

        search_client(lastname='Polson')

        delete_number(1)

        delete_client(1)
