from sqlite3 import Date
import database


def get_servers(query=None):
    return database.query("select * from servers " + (("where " + query) if query else "") + ";")


def add_server(game, name, ip, owner, description, modinfo):
    return database.execute("insert into servers (game, name, ip, owner, description, modinfo, created) values (?, ?, ?, ?, ?, ?, current_timestamp)",
                            (game, name, ip, owner, description, modinfo))
