#!/usr/bin/env python3

"""

"""

import os
import pathlib
import sqlite3
import sys
import time


default = "_"
_rc = pathlib.Path.home() / ".sqliterc"
_rc = _rc.exists() and _rc.read_text()

table_template = """
create table "{}" (
    k primary key,
    v
) without rowid
""".format


class Instances(dict):
    def __missing__(self, key):
        conn = sqlite3.connect(key, 60.0)
        if _rc:
            conn.executescript(_rc)
        self[key] = conn, conn.cursor()
        return self[key]


class KV(object):
    def __init__(self):
        self._instances = Instances()

    def __len__(self):
        return len(self._instances)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            space, key = key
            return self.get(key, space)
        return self.get(key)

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            space, keys = key
            return self.set(key, value, space)
        return self.set(key, value)

    def branch(self, key) -> str:
        "override this"
        return ".kvlite.db"

    def _pick(self, key):
        return self._instances[self.branch(key)]

    def _execute(self, table_name, cursor, sql, *args):
        try:
            cursor.execute(sql, args)
        except sqlite3.OperationalError as e:
            if not e.args[0].startswith("no such table"):
                raise
            cursor.execute(table_template(table_name))
            cursor.execute(sql, args)

    def get(self, key, space=default):
        sql = f"""select v from "{space}" where k = ?"""
        _, c = self._pick(key)
        self._execute(space, c, sql, key)
        o = c.fetchone()
        if o:
            return o[0]

    def set(self, key, value, space=default):
        sql = f"""replace into "{space}" (k, v) values(?, ?)"""
        conn, c = self._pick(key)
        self._execute(space, c, sql, key, value)
        conn.commit()

    def get_many(self, keys, space=default):
        'todo'

    def set_many(self, iterable, space=default):
        sql = f"""replace into "{space}" (k, v) values(?, ?)"""
        todo = set()
        for key, value in iterable:
            conn, c = self._pick(key)
            todo.add(conn)
            self._execute(space, c, sql, key, value)
        for conn in todo:
            conn.commit()

    def patch(self, iterable, space=default):
        """
        """

    def sync(self, iterable, space=default):
        """
        """


if __name__ == '__main__':
    def test():
        db = KV()
        db.set('1', 2, "t")
        db.set(b'1', 3, "t")
        print(db.get('1', "t"))
        print(db["t", '1'])
        db[1] = 2
        print(db[1])
        t0 = time.time()
        for i in range(1_000):
            db.get(2, 't')
        db.set_many(list(zip(range(10000), range(10000, 20000))))
        print(time.time() - t0)
        print(len(db))
    test()
