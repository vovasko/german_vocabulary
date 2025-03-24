import sqlite3
import pandas as pd

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
                type TEXT NOT NULL,
                german TEXT NOT NULL,
                translation TEXT,
                second_translation TEXT,
                example TEXT,
                meaning TEXT,
                score INTEGER NOT NULL DEFAULT 0
            ); """)

            connection.commit()

    def insert_data(self, data: dict | list | pd.DataFrame): # ensure to always form dictionaries 
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient="records")
            template = data[0] if isinstance(data, list) else data # get a dict to use as template

            insert_query = f"""
            INSERT INTO vocabulary ({", ".join(template.keys())})
            VALUES ({", ".join([f":{key}" for key in template.keys() if key != "rowid"])});
            """

            try:
                if isinstance(data, list):
                    cursor.executemany(insert_query, data)
                elif isinstance(data, pd.DataFrame):
                    data_list = data.to_dict(orient="records")
                    cursor.executemany(insert_query, data_list)
                else:
                    cursor.execute(insert_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)

    def update_data(self, data: dict | list | pd.DataFrame): # to bulk update, all columns should be same
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient="records")
            template = data[0] if isinstance(data, list) else data # get a dict to use as template

            set_clause = ", ".join([f"{key}=:{key}" for key in template.keys() if key != "rowid"])
            update_query = f"""
                UPDATE vocabulary
                SET {set_clause}
                WHERE rowid=:rowid;
                """

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
            
    def delete_data(self, data: dict | list | pd.DataFrame):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            delete_query = """
            DELETE FROM vocabulary
            WHERE rowid=:rowid; """

            try:
                if isinstance(data, list):
                    cursor.executemany(delete_query, data)
                elif isinstance(data, pd.DataFrame):
                    data_list = data.to_dict(orient="records")
                    cursor.executemany(delete_query, data_list)
                else:
                    cursor.execute(delete_query, data)
                connection.commit()
            except sqlite3.IntegrityError as e:
                print("IntegrityError:", e)
            except Exception as e:
                print("Error:", e)

    def drop_table(self):
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            cursor.execute("DROP TABLE IF EXISTS vocabulary;")

            connection.commit()
        
    def fetch_data(self, mode: str = "all", just_return_query: bool = False) -> list | str:
        # return either a list of tuples or a query string
        with sqlite3.connect("vocabulary.db") as connection:
            cursor = connection.cursor()

            match mode:
                case "all"       : select_query = "SELECT rowid, * FROM vocabulary;"
                case "duplicates": select_query = """
                                    SELECT * FROM vocabulary
                                    WHERE (type, german) IN (
                                        SELECT type, german FROM vocabulary
                                        GROUP BY type, german
                                        HAVING COUNT(*) > 1
                                    ); """
                case "new"       : select_query = "SELECT rowid, * FROM vocabulary WHERE score = 0;"

            if just_return_query:
                return select_query
            else:
                cursor.execute(select_query)
                return cursor.fetchall()

    def to_dataframe(self, mode: str = "all") -> pd.DataFrame:
        query = self.fetch_data(mode, just_return_query=True) # get query according to given mode
        with sqlite3.connect("vocabulary.db") as connection:
            return pd.read_sql_query(query, connection)
    
    def update_from_df(self, df: pd.DataFrame):
        # Delete rows that were marked for deletion
        delete_condition = df["german"].str.startswith("#delete")
        df_to_delete = df[delete_condition]
        df = df[~delete_condition]

        if not df_to_delete.empty: # delete, if there are rows to delete
            self.delete_data(df_to_delete)

        # Check for rows to update
        if df.empty:
            return

        # Update all rows that are left
        for _, row in df.iterrows():
            try:
                row = row.to_dict()
                self.update_data(row)
            except Exception as e:
                print(f"Error updating record {row['rowid']}: {e}")
        
db = DBManager()
db.create_table()



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
    + insert data (from dict, list, DF)
    + update data (from dict, list)
    + delete data
    + fetcch data
    ?- create a context manager
    ?- create a decorator for the methods


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
