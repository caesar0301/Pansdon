#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Fetch and backup projects of PySpider
# Auther: Xiaming Chen
# Email: chenxm35@gmail.com
##
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


def prettify(code):
	code2 = re.sub(r"\t", "    ", code)
	return code2


def get_spiders():
	db_instance = MDBUtils("projectdb")
	res = db_instance.execute("select * from projectdb;")
	for project in res:
		name = project[0]
		code = project[3]
		
		with open("project_%s.py" % name, 'wb') as of:
			of.write(prettify(code))
			of.close()


if __name__ == '__main__':
	get_spiders()
