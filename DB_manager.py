import sqlite3
from pandas import DataFrame

class DBManager:
    def __init__(self):
        pass

    def create_db(self):
        with sqlite3.connect("vocabulary.db") as connection:
            pass

    def create_table(self):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY,
                type TEXT,
                german TEXT NOT NULL,
                translation TEXT,
                second_translation TEXT,
                example TEXT,
                meaning TEXT,
                score INTEGER NOT NULL DEFAULT 0
            ); """)

            connection.commit()

    def insert_data(self, data: dict | list | DataFrame): # ensure to always form dictionaries 
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO vocabulary (type, german, translation, second_translation, example, meaning, score)
            VALUES (:type, :german, :translation, :second_translation, :example, :meaning, :score); """

            try:
                if isinstance(data, list):
                    cursor.executemany(insert_query, data)
                elif isinstance(data, DataFrame):
                    data_list = data.to_dict(orient="records")
                    cursor.executemany(insert_query, data_list)
                else:
                    cursor.execute(insert_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)

    def update_data(self, data: dict | list):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            update_query = """
            UPDATE vocabulary
            SET type=:type, german=:german, translation=:translation, second_translation=:second_translation,
                example=:example, meaning=:meaning, score=:score
            WHERE id=:id; """

            try:
                if isinstance(data, list):
                    cursor.executemany(update_query, data)
                else:
                    cursor.execute(update_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)
            
    def delete_data(self, data: dict | list):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            delete_query = """
            DELETE FROM vocabulary
            WHERE id=:id; """

            try:
                if isinstance(data, list):
                    cursor.executemany(delete_query, data)
                else:
                    cursor.execute(delete_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)

    def select_data(self, mode: str):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            select_query = """"""
            match mode:
                case "all": select_query = "SELECT * FROM vocabulary;"
                case "new": select_query = "SELECT * FROM vocabulary WHERE score=0;"

            cursor.execute(select_query)

            results = cursor.fetchall()

            return results
    
    def select_duplicates(self):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            select_query = """
            SELECT german, COUNT(german) AS count
            FROM vocabulary
            GROUP BY german
            HAVING count > 1; """

            cursor.execute(select_query)
            return cursor.fetchall()
            
    def drop_table(self):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            cursor.execute("DROP TABLE IF EXISTS vocabulary;")

            connection.commit()
        
    def insert_from_df(self, df): # insert all records from DF

        pass

    def update_from_df(self, df): # does all kind of changes
        """
        save original IDs
        modify DF
        update records in DB with remaining records in DF
        delete records from DB if there are less IDs in DF that before modification
        """
        pass



def main(): 
    db = DBManager()
    db.create_table()

    

if __name__ == "__main__":
    main()

"""
what do i want to do right now?
 - create a class that will manage the database
 - it will 
    + create the database
    + create the table
    + insert data
    + update data
    + delete data
    - query data
    - close the connection
    - create a context manager
    - create a decorator for the methods


What do I need to change in main.py?
 - changes with DFs:
    - function to check for duplicates
    - function to check for missing values
    - function to check for new words (score = 0)
 - come up with an idea to display data in the tables
 - come up with an idea to work with the data in antoher windows:
    - Flash cards:
        - how to update score
        - how to compose a deck
    - Edit mode and Duplicates viewer:
        - how to connect data in table with data in DB
 - need a function to:
    1. Create a pandas DF from the DB with specific data in it 
       df = pd.read_sql_query(select_query, connection)
       it will read all 8 columns (id column + 7 data columns)
    2. Interact with this new DF (change / delete records)
    3. Update the DB with help of modified DF
"""
