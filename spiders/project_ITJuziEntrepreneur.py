#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-01 00:10:46
# Project: ITJuzi
import re

from pyspider.libs.base_handler import *
from bs4 import BeautifulSoup
from bs4.element import Tag
from psdkit.utils import *
from psdkit import ITJuzi


MASTER_URL = 'http://www.itjuzi.com/person'
DBNAME="ITJuzi"
TABLENAME="entrepreneur"
MAX_PAGE = 1699

db_handler = MDBUtils(DBNAME)


def extract_company_id(page):
    match = re.search(r"(?<=company/)\d+", page)
    return int(match.group(0)) if match else -1


def extract_person_id(page):
    match = re.search(r"(?<=person/)\d+", page)
    return int(match.group(0)) if match else -1


class Handler(BaseHandler):
    ## Act as a browser
    headers= {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36"
    }

    crawl_config = {
        "headers" : headers,
        "timeout" : 100
    }
    
    @config(age=24 * 3600)
    def on_start(self):
        self.crawl(MASTER_URL, callback=self.parse_pn)

        
    def parse_pn(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        PAGES = max(MAX_PAGE, ITJuzi.extract_max_page(soup))
        for i in range(1, PAGES + 1):
            self.crawl("%s?page=%d" % (MASTER_URL, i), callback=self.index_page)

            
    @config(age=3 * 24 * 3600)
    def index_page(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        for ul in soup.find_all('ul', class_ = 'list-main-personset', limit=1):
            for li in ul.find_all('li'):
                name = li.find(class_ = 'name')
                if name:
                    pid = extract_person_id(name['href'])
                    self.crawl(name['href'], callback=self.index_person)

                    
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
        db_handler.execute(command)

