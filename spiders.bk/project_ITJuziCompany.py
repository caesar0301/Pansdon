#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-01 00:10:46
# Project: ITJuzi

from pyspider.libs.base_handler import *
from bs4 import BeautifulSoup
import re
from psdkit.utils import *
from psdkit import ITJuzi


MASTER_URL = 'http://www.itjuzi.com/company'
DBNAME="ITJuzi"
TABLENAME="company"
MAX_PAGE = 3427

db_handler = MDBUtils(DBNAME)


def extract_company_id(self, page):
    match = re.search(r"(?<=company/)\d+", page)
    return int(match.group(0)) if match else -1


class Handler(BaseHandler):
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
    
    
    @config(age=3 * 24 * 60 * 60)
    def on_start(self):
        # Extract the max number of pages
        self.crawl(MASTER_URL, callback=self.parse_pn)
        
        
    @config(age=3 * 24 * 60 * 60)
    def parse_pn(self, response):
        soup = BeautifulSoup(response.text, "html5lib")
        PAGES = max(ITJuzi.extract_max_page(soup), MAX_PAGE)
        for i in range(1, PAGES + 1):
            self.crawl("%s?page=%d" % (MASTER_URL, i), callback=self.index_company)


    @config(age=3 * 24 * 60 * 60)
    def index_company(self, response):
        soup = BeautifulSoup(response.text, "html5lib")

        companies = []
        for ul in soup.find_all('ul', class_ = 'list-main-icnset'):
            if (len(ul['class']) > 1): # skip table title
                continue
            # Find all table rows, each row a company
            for li in ul.find_all('li', recursive=False):
                # Process each table cell
                result = {}
                for i in li.find_all('i', class_=lambda x: 'cell' in x):
                    cell_type = i['class'][1]
                    if cell_type == 'pic':
                        image = i.find('img')
                        company_pic = image['src'] if image is not None else ""
                        company_page = i.a['href']
                        result['pic'] = company_pic
                        result['page'] = company_page
                        result['id']  = self.extract_company_id(company_page)

                    if cell_type == 'date':
                        company_date = i.string.strip('\t \n')
                        result['birth'] = company_date

                    if cell_type == 'maincell':
                        company_title = i.find('p', class_="title").string
                        company_description = i.find('p', class_="des").string
                        company_tag = i.find('span', class_ = "tags").a.string
                        company_local = i.find('span', class_ = "loca").a.string
                        result['title'] = company_title
                        result['description'] = company_description
                        result['tag'] = company_tag
                        result['local'] = company_local

                    if cell_type == 'round':
                        company_round = i.span.string.strip('\t \n')
                        result['round'] = company_round
                companies.append(result)
        return companies
    
    
    def on_result(self, companies):
        if companies is None:
            return
        
        for r in companies:
            print(r)
            command = assemble_insert_cmd(r, DBNAME+"."+TABLENAME, {
            'id': 'id',
            'title': 'title',
            'description': 'description',
            'tag': 'tag',
            'local': 'local',
            'round': 'round',
            'birth': 'birth',
            'page': 'page',
            'pic': 'pic'
            })

            print(command)
            db_handler.execute(command)

