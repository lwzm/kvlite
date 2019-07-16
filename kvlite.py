#!/usr/bin/env python3

"""

"""

import os
import pathlib
import sqlite3
import sys
import time


data_dir = pathlib.Path(os.getenv("KVLITE_DATA", ".data"))
data_dir.mkdir(parents=True, exist_ok=True)


table_template = """
create table {} (
    k primary key,
    v
)
""".format


class Instances(dict):
    def __missing__(self, key):
        conn = sqlite3.connect(data_dir / key)
        self[key] = conn
        return conn


class KV(object):
    def __init__(self):
        self._instances = Instances()

    def branch(self, key) -> str:
        "override this"
        return "this_is_test.db"

    def _execute(self, scope, cursor, sql, args):
        while True:
            try:
                cursor.execute(sql, args)
                break
            except sqlite3.OperationalError as e:
                if e.args[0].startswith("no such table"):
                    cursor.execute(table_template(scope))
                else:
                    raise e

    def get(self, scope, key):
        sql = f"select v from {scope} where k = ?"
        c = self._instances[self.branch(key)].cursor()
        self._execute(scope, c, sql, (key,))
        o = c.fetchone()
        if o:
            return o[0]

    def set(self, scope, key, value):
        sql = f"insert or replace into {scope} (k, v) values(?, ?)"
        conn = self._instances[self.branch(key)]
        self._execute(scope, conn.cursor(), sql, (key, value))
        conn.commit()

    def get_many(self, scope, keys):
        'todo'

    def set_many(self, scope, keys, values):
        'todo'


if __name__ == '__main__':
    def test():
        db = KV()
        db.set("t", '1', 2)
        db.set("t", b'1', 3)
        print(db.get('t', '1'))
    test()
