from migrations.Site import Site as SiteDef


class Site:
    def __init__(self, name, host):
        self.name = name
        self.host = host

    # def get_all_sites(self):
    #     session = Database.get_session()
    #     return session.query(SiteDef).all()
