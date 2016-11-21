#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-06 00:07:21
# Project: ITJuziInvest
import re
from pyspider.libs.base_handler import *
from psdkit.utils import *
from psdkit import ITJuzi
from bs4 import BeautifulSoup
from bs4.element import Tag


MASTER_URL = 'http://www.itjuzi.com/investevents'
DBNAME="ITJuzi"
TABLENAME="invests"
MAX_PAGE_DOM = 1461
MAX_PAGE_FOR = 405
TYPE_DOM = 0
TYPE_FOR = 1
db_handler = MDBUtils(DBNAME)


def extract_event_id(page):
    match = re.search(r"(?<=investevents/)\d+", page)
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
    
    
    @every(minutes=24 * 60)
    def on_start(self):
        # Determine the max page number first
        self.crawl(MASTER_URL, callback = self.parse_max_page, save={"type": TYPE_DOM})
        self.crawl(MASTER_URL+"/foreign", callback = self.parse_max_page, save={"type": TYPE_FOR})
        

    def parse_max_page(self, response):
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

            
    @config(age=3 * 24 * 60 * 60, priority = 10)
    def index_page(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        
        events = []
        table = soup.find_all("ul", class_ = "list-main-eventset")
        for t in table:
            ## Skip table head
            if 'thead' in t['class']: continue
            
            for entry in t.find_all('li'):
                investe = {'type': response.save['type'] if response.save else -1}
                
                for cell in entry.find_all('i', class_ = 'cell'):
                    ctype = cell['class'][1]                   
                    
                    if ctype == 'round':
                        if cell.find('span', class_ = 'tag'):
                            investe['round'] = clean(cell.text)
                        else:
                            investe['time'] = clean(cell.text)
                        
                    elif ctype == 'pic':
                        img = cell.find('a', href=True)
                        if img:
                            investe['id'] = extract_event_id(img['href'])
                            
                    elif ctype == 'maincell':
                        title = cell.find('p', class_ = 'title')
                        if title:
                            investe['title'] = clean(title.text)
                        tags = cell.find('span', class_ = 'tags')
                        if tags:
                            investe['tags'] = clean(tags.text)
                        loc = cell.find('span', class_ = 'loca')
                        if loc:
                            investe['loc'] = clean(loc.text)
                            
                    elif ctype == 'fina':
                        investe['financing'] = clean(cell.text)

                    investors = cell.find('span', class_ = 'investorset')
                    if investors: investe['investors'] = \
                        '|'.join([clean(i) for i in investors.strings if clean(i) != ""])

                events.append(investe)
        return events
            
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
            'round': 'round',
            'financing': 'financing',
            'investors': 'investors',
            'type': 'type'
            })
            
            print(command)
            db_handler.execute(command)
