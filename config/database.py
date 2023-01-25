import os


database_name = 'screenshots'
database = os.path.join(os.path.dirname('storage/'), f"{database_name}.sqlite3")
conn_string = f'sqlite:///{database}'
