from migrations.Site import Site as SiteDef
from models.Database import Database


class Response:
    def __init__(self, content):
        self.content = content
