from pymongo import MongoClient
from .ES_connector import *
from .QUERY_DICT import get_newly_added_query,mark_added_query,get_collection,generate_bulk_query

es = get_es_conn()
collection = None

def __insert_ES_mark_mongo(_newly_records,_newly_ids):
    bulk_q = generate_bulk_query(_newly_records,'arxiv')
    if bulk_q:
        es.bulk(bulk_q)
        _filter_query,_update_query = mark_added_query(_newly_ids)
        collection.update_many(_filter_query,_update_query)
        print('insert {} record.'.format(len(_newly_records)))
    

def update_ES_from_arxiv(index:str):
    _QUERY = get_newly_added_query(index)
    global collection
    collection = get_collection(index)

    # _newly_cursor = arxiv.find(_QUERY,limit = 500)
    _newly_cursor = collection.find(_QUERY).batch_size(2000) #set baatch_size, the cursor will get 500 each time access the mongo

    #maintain the ids and the field we needed
    _newly_ids = []
    _newly_records = []
    for record in _newly_cursor:
        _newly_ids.append(record['_id'])
        _newly_records.append(record)
        if len(_newly_records) == 2000:
            # insert into ES
            #update the mongo mark
            __insert_ES_mark_mongo(_newly_records,_newly_ids)
            _newly_records=[]
            _newly_ids = []    
    else:
        __insert_ES_mark_mongo(_newly_records,_newly_ids)
            
    # part below is insert a single doc one time
    # _newly_ids = []
    # for record in _newly_cursor:
    #     _newly_ids.append(record['_id'])
    #     record = {'abstrct':record['abstract'],'title':record['title']}
    #     es.index(index = 'test-index',doc_type='paper',body = record)
    #     if len(_newly_ids) == 500:
    #         _filter_query,_update_query = mark_added_query(_newly_ids)
    #         arxiv.update_many(_filter_query,_update_query)
    #         _newly_ids = []
    # else:
    #     _filter_query,_update_query = mark_added_query(_newly_ids)
    #     arxiv.update_many(_filter_query,_update_query)




if __name__ == '__main__':
    collections = ['arxiv','news','github']
    for _index in collections:
        update_ES_from_arxiv(_index)        