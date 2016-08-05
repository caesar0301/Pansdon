#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-01 00:10:46
# Project: ITJuzi
import re

from pyspider.libs.base_handler import *
from bs4 import BeautifulSoup
from bs4.element import Tag
import MySQLdb as mdb


MASTER_URL = 'http://www.itjuzi.com/person'
DBNAME="ITJuzi"
TABLENAME="entrepreneur"
MAX_PAGE = 1699


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

db_handler = MDBUtils(DBNAME)


def extract_company_id(page):
    match = re.search(r"(?<=company/)\d+", page)
    return int(match.group(0)) if match else -1


def extract_person_id(page):
    match = re.search(r"(?<=person/)\d+", page)
    return int(match.group(0)) if match else -1


def append_str(origin, newstr, sep='|'):
    strings = [origin, newstr]
    return sep.join([ i for i in strings if len(i) > 0])


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
            values.append('"%s"' % result[rkey])
        else:
            values.append(str(result[rkey]))
    values_str = '(' + ','.join(values) + ')'

    # Assemble update assignment string, e.g., a=v1,b=v2
    updates = [''.join(list(i)) for i in zip(columns, list("=") * len(values), values)]
    update_str = ','.join(updates)

    command = "INSERT INTO %s %s VALUES %s ON DUPLICATE KEY UPDATE %s;" % \
        (table_name, columns_str, values_str, update_str)
    return command
    

class Handler(BaseHandler):
    ## Act as a browser
    headers= {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"
    }

    crawl_config = {
        "headers" : headers,
        "timeout" : 100
    }
    
    @config(age=3 * 24 * 3600)
    def on_start(self):
        for i in range(1, MAX_PAGE + 1):
            self.crawl("%s?page=%d" % (MASTER_URL, i), callback=self.index_page)

            
    @config(age=3 * 24 * 3600)
    def index_page(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        for ul in soup.find_all('ul', class_ = 'list-main-personset', limit=1):
            for li in ul.find_all('li'):
                name = li.find(class_ = 'name')
                if name:
                    pid = extract_person_id(name['href'])
                    self.crawl(name['href'], callback=self.index_person, save={'id': pid})

                    
    @config(age=3 * 24 * 3600, priority=10)
    def index_person(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        person_info = {}
        
        # Extract person ID
        a_pid = soup.find(id='loginurl')
        if a_pid:
            pid = extract_person_id(a_pid['href'])
        else:
            pid = -1
        person_info['id'] = pid
        
        # Extract head and titles
        infohead = soup.find_all('div', class_ = "infohead-person")[0]
        
        # Each piece of info stored in a <p> tag
        for p in infohead.find_all('p'):
            ## Person name
            span = p.find('span', class_ = "name")
            if span is not None:
                person_info['name'] = span.text
            
            ## Person titles
            class_attrs = p.attrs.get('class')
            if class_attrs and "titleset" in class_attrs:
                titleset = []
                for span in p.find_all('span'):
                    cnum = extract_company_id(span.a['href'])
                    cname = span.a.string
                    title = span.text
                    titleset.append("%s,%d,%s" % (cname, cnum, title))
                person_info['title'] = '|'.join(titleset)
            
            ## Person location
            mapitem = p.find('i', class_ = re.compile('map-marker'))
            if mapitem:
                person_info['loc'] = re.sub(r'(\s+)?\xb7(\s+)?', ';', p.text.strip('\t \n'))
                
        # Brief intro and experience
        for main in soup.find_all('div',class_ = "main"):
            for sec in main.find_all('div', class_ = "titlebar"):
                sec_title = sec.text.strip('\r\n\t ')
                print("TITLE===========" + sec_title)
                
                if sec_title == u"创业者简介":
                    intro = u""
                    for sibling in sec.next_siblings:
                        if not isinstance(sibling, Tag):
                            c = sibling.strip('\r\n\t ')
                        else:
                            c = sibling.text.strip('\r\n\t ')
                        intro = append_str(intro, c)
                    person_info['intro'] = intro
                    print(intro)
                    
                if sec_title == u'创业经历':
                    person_info['exp_startup'] = ''
                    
                if sec_title == u'工作经历':
                    intro = u""
                    for sibling in sec.next_siblings:
                        if not isinstance(sibling, Tag):
                            c = sibling.strip('\r\n\t ')
                        else:
                            c = sibling.text.strip('\r\n\t ')
                        intro = append_str(intro, c)
                    person_info['exp_work'] = intro
                    print(intro)
                    
                if sec_title == u'教育经历':
                    intro = []
                    for sibling in sec.next_siblings:
                        if not isinstance(sibling, Tag):
                            continue
                        cinfo = u""
                        ## a college list
                        colleges = sibling.find_all('li')
                        if len(colleges) > 0:
                            for college in colleges:
                                c = college.text.strip('\r\n\t ')
                                cinfo = append_str(cinfo, c)
                        else:
                            c = sibling.text.strip('\r\n\t ')
                            cinfo = append_str(cinfo, c)
                        intro.append(cinfo)
                    person_info['exp_edu'] = '\n'.join(intro)
                    print(person_info['exp_edu'])
                    
        return person_info
    
    def on_result(self, r):
        if r is None:
            return
        
        command = assemble_insert_cmd(r, DBNAME+"."+TABLENAME, {
        'id': 'id',
        'name': 'name',
        'title': 'title',
        'loc': 'location',
        'intro': 'intro',
        'exp_startup': 'exp_startup',
        'exp_work': 'exp_work',
        'exp_edu': 'exp_edu'
        })
        print(command)

        try:
            db_handler.execute(command)
        except Exception, e:
            print(e)
