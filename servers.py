import database
from datetime import datetime
from user import get_by_username


dateFormat = ''


class Server:
    def __init__(self, sid, game, name, ip, owner, description, created):
        self.sid = sid
        self.game = game
        self.name = name
        self.ip = ip
        self.owner = owner
        self.owner_user = get_by_username(owner)
        self.description = description
        self.created = created
        self.createdTime = datetime.strptime(
            created, '%Y-%m-%d %H:%M:%S').strftime('%d %b, %Y')


def get_server_by_id(id):
    result = database.query(f"select * from servers where id = '{id}';",
                            one=True)
    server = Server(sid=result["ID"],
                    game=result["game"],
                    name=result["name"],
                    ip=result["ip"],
                    owner=result["owner"],
                    description=result["description"],
                    created=result["created"])
    return server


def get_server(name):
    result = database.query(f"select * from servers where name = '{name}';",
                            one=True)
    server = Server(sid=result["ID"],
                    game=result["game"],
                    name=result["name"],
                    ip=result["ip"],
                    owner=result["owner"],
                    description=result["description"],
                    created=result["created"])
    return server


def get_all_servers(query=None):
    servers = []
    for result in database.query("select * from servers " + (("where " + query) if query else "") + ";"):
        servers.append(Server(sid=result["ID"],
                              game=result["game"],
                              name=result["name"],
                              ip=result["ip"],
                              owner=result["owner"],
                              description=result["description"],
                              created=result["created"]))
    return servers


def add_server(game, name, ip, owner, description, modinfo):
    return database.execute("insert into servers (game, name, ip, owner, description, created) values (?, ?, ?, ?, ?, current_timestamp)",
                            (game, name, ip, owner, description))


def edit_server(id, game, name, ip, description):
    return database.execute("update servers set game = ?, name = ?, ip = ?, description = ? where id = ?",
                            (game, name, ip, description, id))
