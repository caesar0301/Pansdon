#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-05-15 12:25:23
# Project: awesome_users
import sys

from pyspider.libs.base_handler import *
from pyspider.libs.awesome import MyDB
from pyspider.libs.awesome.config import GITHUB_OAUTH_CLIENT_ID, GITHUB_OAUTH_CLIENT_SCR

reload(sys)
sys.setdefaultencoding('utf8')

# Github API
GITHUB_API='https://api.github.com'
AWESOME='caesar0301/awesome-public-datasets'
DEFAULT_PARAMS={
    'client_id': GITHUB_OAUTH_CLIENT_ID,
    'client_secret': GITHUB_OAUTH_CLIENT_SCR
}


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

    
    @every(minutes=3 * 24 * 60)
    def on_start(self):
        ''' Retrieve basic info. of awesome project
        '''
        self.crawl('%s/repos/%s' % (GITHUB_API, AWESOME),
                   callback=self.crawl_awesome, params=DEFAULT_PARAMS)
    
    
    @config(age=7 * 24 * 3600)
    def crawl_awesome(self, response):
        ''' Crawl the list of stargazers
        '''
        stargazers_count = response.json['stargazers_count']        
        count_per_page = 50
        page_num = stargazers_count / count_per_page + 1
        
        stargazers='%s/repos/%s/stargazers' % (GITHUB_API, AWESOME)
        
        for p in range(1, page_num + 1):
            pars = {'page': p, 'per_page': count_per_page}
            pars.update(DEFAULT_PARAMS)
            self.crawl(stargazers, callback=self.parse_users, params=pars)
    
    
    @config(age=7 * 24 * 3600)
    def parse_users(self, response):
        ''' Parse complete user info.
        '''
        if len(response.json) == 0:
            return
        
        for user in response.json:
            detailed_user = '%s/users/%s' % (GITHUB_API, user['login'])
            self.crawl(detailed_user, callback=self.detailed_user, params=DEFAULT_PARAMS)
    
    
    def detailed_user(self, response):
        info = response.json
        details = {
            'login': info.get('login'),
            'id': info.get('id'),
            'avatar_url': info.get('avatar_url', None),
            'gravatar_id': info.get('gravatar_id', None),
            'name': info.get('name', None),
            'company': info.get('company', None),
            'blog':  info.get('blog', None),
            'location': info.get('location', None),
            'email': info.get('email', None),
            'hireable': info.get('hireable', False),
            'bio': info.get('bio', None),
            'public_repos': info.get('public_repos', 0),
            'public_gists': info.get('public_gists', 0),
            'followers': info.get('followers', 0),
            'following': info.get('following', 0),
            'created_at': info.get('created_at', None),
            'updated_at': info.get('updated_at', None),
        }
        return details
    
    
    def on_result(self, result):
        ''' Dump to database
        '''
        if not result or not result['id']:
            return 

        sql = '''INSERT INTO awesome.users (login, id, avatar_url, gravatar_id, name, company, blog, location, email, hireable, bio, public_repos, public_gists, followers, following, created_at, updated_at) VALUES ("%s", %d, "%s", "%s", "%s", "%s", "%s", "%s", "%s", %d, "%s", %d, %d, %d, %d, "%s", "%s") ON DUPLICATE KEY UPDATE avatar_url = "%s", gravatar_id = "%s", name = "%s", company = "%s", blog = "%s", location = "%s", email = "%s", hireable = %d, bio = "%s", public_repos = %d, public_gists = %d, followers = %d, following = %d, updated_at = "%s"''' % (
            # Insert new fields
            result['login'],
            result['id'],
            result['avatar_url'],
            result['gravatar_id'],
            result['name'],
            result['company'],
            result['blog'],
            result['location'],
            result['email'],
            bool(result['hireable']),
            result['bio'],
            result['public_repos'],
            result['public_gists'],
            result['followers'],
            result['following'],
            result['created_at'],
            result['updated_at'],
            # Update fields
            result['avatar_url'],
            result['gravatar_id'],
            result['name'],
            result['company'],
            result['blog'],
            result['location'],
            result['email'],
            bool(result['hireable']),
            result['bio'],
            result['public_repos'],
            result['public_gists'],
            result['followers'],
            result['following'],
            result['updated_at']
        )
        
        print(sql)
        db = MyDB()
        db.execute(sql)
        db.con.commit()
