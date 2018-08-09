#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient

ip = 'localhost'
port = 27017

client = MongoClient(ip, port)
db = client['DAND']


# insert documents in mongodb database
def db_insert(data, collection):
    db[collection].insert_many(data)

