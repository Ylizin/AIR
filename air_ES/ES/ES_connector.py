from elasticsearch import Elasticsearch as ELS
from pymongo import MongoClient

__conn = MongoClient('mongodb://root:boyu42@localhost')

# __conn = MongoClient('mongodb://root:boyu42@106.75.229.123')
__spider = __conn.spider
__user = __conn.mongodb_42
__ARXIV = __spider.arxiv
__NEWS = __spider.news
__USER = __user.account_userprofile

collection_dicts={
    'arxiv':__ARXIV,
    'news':__NEWS,
    'user':__USER
}

def get_arxiv_collection():
    return __ARXIV

def get_user_collection():
    return __USER

def get_es_conn():
    return ELS()

def get_collection(index):
    return collection_dicts.get(index,None)