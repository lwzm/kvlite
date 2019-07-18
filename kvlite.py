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

_rc = pathlib.Path.home() / ".sqliterc"
_rc = _rc.exists() and _rc.read_text()

table_template = """
create table "{}" (
    k primary key,
    v
)
""".format


class Instances(dict):
    def __missing__(self, key):
        conn = sqlite3.connect(data_dir / key)
        if _rc:
            conn.executescript(_rc)
        self[key] = conn
        return conn


class KV(object):
    def __init__(self):
        self._instances = Instances()

    def __len__(self):
        return len(self._instances)

    def branch(self, key) -> str:
        "override this"
        return "default.db"

    def __getitem__(self, key):
        if isinstance(key, tuple):
            key, space = key
            return self.get(key, space)
        return self.get(key)

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            key, space = key
            return self.set(key, value, space)
        return self.set(key, value)

    def _execute(self, table_name, cursor, sql, *args):
        while True:
            try:
                cursor.execute(sql, args)
                break
            except sqlite3.OperationalError as e:
                if e.args[0].startswith("no such table"):
                    cursor.execute(table_template(table_name))
                else:
                    raise e

    def get(self, key, space="_"):
        sql = f"""select v from "{space}" where k = ?"""
        c = self._instances[self.branch(key)].cursor()
        self._execute(space, c, sql, key)
        o = c.fetchone()
        if o:
            return o[0]

    def set(self, key, value, space="_"):
        sql = f"""insert or replace into "{space}" (k, v) values(?, ?)"""
        conn = self._instances[self.branch(key)]
        self._execute(space, conn.cursor(), sql, key, value)
        conn.commit()

    def get_many(self, keys, space="_"):
        'todo'

    def set_many(self, lst, space="_"):
        sql = f"""insert or replace into "{space}" (k, v) values(?, ?)"""
        todo = set()
        for key, value in lst:
            conn = self._instances[self.branch(key)]
            todo.add(conn)
            c = conn.cursor()
            self._execute(space, c, sql, key, value)
        for conn in todo:
            conn.commit()


if __name__ == '__main__':
    def test():
        db = KV()
        db.set('1', 2, "t")
        db.set(b'1', 3, "t")
        print(db.get('1', "t"))
        print(db['1', "t"])
        db[1] = 2
        print(db[1])
        t0 = time.time()
        for i in range(1_000):
            db.get(2, 't')
        db.set_many(list(zip(range(10000), range(10000, 20000))))
        print(time.time() - t0)
        print(len(db))
    test()
