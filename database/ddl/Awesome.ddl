create database awesome;
alter database awesome character set utf8;

use awesome;

create table if not exists data_items (
	id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(1024),
	intro_short TEXT,
	intro_long LONGTEXT,
	keywords TEXT,
	category VARCHAR(64),
	project_url VARCHAR(1024),
	project_url2 VARCHAR(1024),
	project_url3 VARCHAR(1024),
	data_url VARCHAR(1024),
	data_url2 VARCHAR(1024),
	data_url3 VARCHAR(1024),
	doi VARCHAR(256),
	admin VARCHAR(1024),
	added_time TIMESTAMP NULL,
	updated_time TIMESTAMP NULL
);


-- Define the table of storing Github users related to our awesome project.
-- Three types of users are contained here, i.e. stargazers, contributors, subscribers.
create table if not exists stargazers (
       login VARCHAR(256) NOT NULL,
       id BIGINT PRIMARY KEY,
       avatar_url VARCHAR(1024),
       gravatar_id VARCHAR(256),
       name VARCHAR(256),
       company VARCHAR(256),
       blog VARCHAR(1024),
       location VARCHAR(256),
       email VARCHAR(128),
       hireable BOOL,
       bio VARCHAR(10240),
       public_repos INT DEFAULT 0,
       public_gists INT DEFAULT 0,
       followers INT DEFAULT 0,
       following INT DEFAULT 0,
       created_at VARCHAR(64) NULL,
       updated_at VARCHAR(64) NULL
);
