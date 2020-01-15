import os


# TODO: Check that correct database is being referenced and working properly
database_name = 'screenshots'
database = os.path.join(os.path.dirname('../storage/'), f"{database_name}.sqlite3")
conn_string = f'sqlite:///{database}'
