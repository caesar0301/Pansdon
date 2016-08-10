# encoding: utf-8
import MySQLdb as mdb
import re

class MDBUtils(object):
    """ Utility to elimitate the burden of interacting with mysql database
    """
    def __init__(self, database, host='localhost', user='root', password='password'):
        self.con = mdb.connect(host, user, password, database)
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


def append_str(origin, newstr, sep='|'):
    strings = [origin, newstr]
    return sep.join([ i for i in strings if len(i) > 0])


def escape_quote(newstr):
	""" Escaping double quotations (both ascii and unicode) into \ascii
	"""
	return re.sub('\"|“|”', '\\\"', newstr, flags=re.U)


def clean(newstr):
    return newstr.strip("\r\n\t ")


def assemble_insert_cmd(result, table_name, column_map):
    # Omit columns that are not in result
    items = [i for i in column_map.items() if i[0] in result]
    
    # Assemble column name tuple
    columns = [str(i[1]) for i in items]
    columns_str = '(' + ','.join(columns) + ')'

    # Assemble values tuple
    values = []
    for rkey, col in items:
        if isinstance(result[rkey], str) or isinstance(result[rkey], unicode):
            # Add double quote to string while escaping the inner quotes
            values.append('"%s"' % escape_quote(result[rkey]))
        else:
            values.append(str(result[rkey]) if result[rkey] is not None else 'NULL')
    values_str = '(' + ','.join(values) + ')'

    # Assemble update assignment string, e.g., a=v1,b=v2
    updates = [''.join(list(i)) for i in zip(columns, list("=") * len(values), values)]
    update_str = ','.join(updates)

    command = "INSERT INTO %s %s VALUES %s ON DUPLICATE KEY UPDATE %s;" % \
        (table_name, columns_str, values_str, update_str)
    return command


if __name__ == "__main__":
    print(escape_quote('hello "world"'))
    print(escape_quote('用户通过“享在家"'))
