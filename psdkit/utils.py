import MySQLdb as mdb

from config import DB_HOST, DB_USER, DB_PASSWD, DB_NAME


class MyDB(object):

    def __init__(self):
        self.con = mdb.connect(DB_HOST, DB_USER, DB_PASSWD, DB_NAME)
        self.con.set_character_set('utf8')
        self.cur = self.con.cursor()
        self.cur.execute('SET NAMES utf8;')
        self.cur.execute('SET CHARACTER SET utf8;')
        self.cur.execute('SET character_set_connection=utf8;')

    def __del__(self):
        self.con.commit()
        self.cur.close()
        self.con.close()

    def execute(self, sql_cmd, n=None):
        self.cur.execute(sql_cmd)
        self.con.commit()
        if n is None:
            return self.cur.fetchall()
        return self.cur.fetchmany(n)


if __name__ == '__main__':
    mydb = MyDB()
    print(mydb.execute('SELECT id,name FROM data_items ORDER by ID'))
