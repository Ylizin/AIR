from elasticsearch import Elasticsearch as ELS

def get_es_conn():
    return ELS()