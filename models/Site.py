from migrations.Site import Site as SiteDef
from models.Database import Database

sites = [
    {"name": "airbnb", "url": "https://www.airbnb.com"},
    {"name": "lewagon", "url": "https://www.lewagon.com"},
    {"name": "evercheck", "url": "https://evercheck.com"},
    {"name": "evolt", "url": "https://evolt.io"},
    {"name": "uscreen-leadzen", "url": "https://uscreen.tv/leadzen"},
    {"name": "generated", "url": "https://generated.photos"},
    {"name": "quokka", "url": "https://quokka.io"},
    {"name": "supercast", "url": "https://supercast.com"},
    {"name": "upcut", "url": "https://upcutstudio.com"},
    {"name": "liramail", "url": "https://liramail.com"},
    {"name": "webflow", "url": "https://webflow.com"},
    {"name": "envoyer", "url": "https://envoyer.io"},
    {"name": "sizzy", "url": "https://sizzy.co"},
    {"name": "forge", "url": "https://forge.laravel.com"},
    {"name": "vapor", "url": "https://vapor.laravel.com"},
    {"name": "nova", "url": "https://nova.laravel.com"},
    {"name": "todoist", "url": "https://todoist.com"},
    {"name": "wire", "url": "https://wire.com"},
    {"name": "wake", "url": "https://wake.com"},
    {"name": "glyph", "url": "https://glyph.pro"},
    {"name": "stripe-connect", "url": "https://stripe.com/connect"},
    {"name": "slack", "url": "https://slack.com"},
    {"name": "makeitinua", "url": "https://makeitinua.com"},
    {"name": "pitch", "url": "https://pitch.com"},
    {"name": "stripe", "url": "https://stripe.com"},
    {"name": "designcode", "url": "https://designcode.io"},
    {"name": "atlassian", "url": "https://atlassian.com"},
    {"name": "forestadmin", "url": "https://forestadmin.com"},
    {"name": "lattice", "url": "https://lattice.com"},
    {"name": "stripe-atlas", "url": "https://stripe.com/atlas"},
    {"name": "evrybo", "url": "https://evrybo.com"},
    {"name": "reddit", "url": "https://reddit.com"},
    {"name": "lobe", "url": "https://lobe.ai"},
]


class Site:
    def __init__(self, name, host):
        self.name = name
        self.host = host

    def get_all_sites(self):
        session = Database.get_session()
        return session.query(SiteDef).all()
