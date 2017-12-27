import json
import pymysql

with open("./mysql.json", "r") as f:
    config = json.load(f)

def connect():
    connection = pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db=config['db'], charset='utf8')
    connection.autocommit(True)
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    return connection, cursor

def execute(connection, cursor, sql, args=None):
    try:
        cursor.execute(sql, args) if args is not None else cursor.execute(sql)
        return cursor
    except pymysql.err.OperationalError:
        connection.connect()
        return execute(sql, args)