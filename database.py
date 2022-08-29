import mysql.connector
import os

config = {
    'user': os.getenv("dbuser"),
    'password': os.getenv("dbpasswd"),
    'host': '127.0.0.1',
    'database': 'website',
    'raise_on_warnings': True
}


def execute(query, args=()):
    with mysql.connector.connect(**config) as cnx:
        cursor = cnx.cursor()
        res = cursor.execute(query, args)
        cnx.commit()
        return res


def query(query, args=(), one=False):
    with mysql.connector.connect(**config) as cnx:
        cursor = cnx.cursor()
        cursor.execute(query, args)
        r = [dict((cursor.description[i][0], value)
                  for i, value in enumerate(row)) for row in cursor.fetchall()]
        cnx.commit()
        return (r[0] if r else None) if one else r
