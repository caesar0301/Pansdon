#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-10 15:19:08
# Project: ITjuziMerge

import re

from pyspider.libs.base_handler import *
from bs4 import BeautifulSoup
from bs4.element import Tag
from psdkit.utils import *
from psdkit import ITJuzi

MASTER_URL = 'http://www.itjuzi.com/merger'
DBNAME="ITJuzi"
TABLENAME="mergers"
MAX_PAGE_DOM = 94
MAX_PAGE_FOR = 64
TYPE_DOM = 0
TYPE_FOR = 1

db_handler = MDBUtils(DBNAME)


def extract_merger_id(page):
    match = re.search(r"(?<=merger/)\d+", page)
    return int(match.group(0)) if match else -1


class Handler(BaseHandler):
    
    ## Act as a browser
    headers= {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,zh-CN;q=0.8,zh;q=0.5,en;q=0.3",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
    }

    crawl_config = {
        "headers" : headers,
        "timeout" : 100
    }

    @every(minutes=24 * 60)
    def on_start(self):
        # Determine the max page number first
        self.crawl(MASTER_URL, callback = self.parse_pn, save={"type": TYPE_DOM})
        self.crawl(MASTER_URL+"/foreign", callback = self.parse_pn, save={"type": TYPE_FOR})

    
    def parse_pn(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        
        if response.save["type"] == TYPE_DOM:
            DOM = max(ITJuzi.extract_max_page(soup), MAX_PAGE_DOM)
            for i in range(1, DOM + 1):
                self.crawl("%s?page=%d" % (MASTER_URL, i),
                           callback=self.index_page, save=response.save)
                
        if response.save["type"] == TYPE_FOR:
            FOR = max(ITJuzi.extract_max_page(soup), MAX_PAGE_FOR)
            for i in range(1, FOR + 1):
                self.crawl("%s?page=%d" % (MASTER_URL+"/foreign", i),
                           callback=self.index_page, save=response.save)


    @config(age=3 * 24 * 60 * 60)
    def index_page(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        
        events = []
        table = soup.find_all("ul", class_ = "list-main-eventset")
        for t in table:
            ## Skip table head
            if 'thead' in t['class']: continue
            
            for entry in t.find_all('li'):
                E = {'type': response.save['type'] if response.save else -1}
                
                for cell in entry.find_all('i', class_ = 'cell'):
                    ctype = cell['class'][1]                   
                    
                    if ctype == 'round':
                        if cell.find('span', class_ = 'tag'):
                            E['stock'] = clean(cell.text)
                        else:
                            E['time'] = clean(cell.text)
                        
                    elif ctype == 'pic':
                        img = cell.find('a', href=True)
                        if img:
                            E['id'] = extract_merger_id(img['href'])
                            
                    elif ctype == 'maincell':
                        title = cell.find('p', class_ = 'title')
                        if title:
                            E['title'] = clean(title.text)
                        tags = cell.find('span', class_ = 'tags')
                        if tags:
                            E['tags'] = clean(tags.text)
                        loc = cell.find('span', class_ = 'loca')
                        if loc:
                            E['loc'] = clean(loc.text)
                            
                    elif ctype == 'fina':
                        E['financing'] = clean(cell.text)
                        
                    elif ctype == 'date':
                        E['merger'] = clean(cell.text)

                events.append(E)
        return events


    @config(priority=2)
    def on_result(self, response):
        if response is None:
            return
        
        for r in response:
            command = assemble_insert_cmd(r, DBNAME+"."+TABLENAME, {
            'id': 'id',
            'title': 'name',
            'loc': 'location',
            'tags': 'tags',
            'time': 'time',
            'stock': 'stock',
            'financing': 'financing',
            'merger': 'merger',
            'type': 'type'
            })
            
            print(command)
            db_handler.execute(command)
