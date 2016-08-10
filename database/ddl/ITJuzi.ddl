-- Database
create database if not exists ITJuzi;
alter database ITJuzi character set utf8;

use ITJuzi;

-- Company dimensions
create table if not exists company (
    id BIGINT NOT NULL PRIMARY KEY,
    title varchar(128),
    description TEXT,
    tag varchar(64),
    local varchar(64),
    round varchar(64),
    birth varchar(64),
    page varchar(256),
    pic varchar(256),
    updated TIMESTAMP
);


-- Person dimensions
create table if not exists entrepreneur (
    id BIGINT NOT NULL PRIMARY KEY,
    name varchar(64),
    title varchar(256),
    location varchar(256),
    intro TEXT,
    exp_startup varchar(1024),
    exp_work varchar(1024),
    exp_edu varchar(1024),
    updated TIMESTAMP
);


-- Invest events
create table if not exists invests (
    id BIGINT NOT NULL PRIMARY KEY,
    name varchar(64),
    location varchar(256),
    tags varchar(256),
    time varchar(64),
    round varchar(64),
    financing varchar(64),
    investors varchar(512),
    updated TIMESTAMP
);

alter table invests add type TINYINT;
