from pymongo import MongoClient
from .ES_connector import *
from .QUERY_DICT import get_newly_added_query,mark_added_query,generate_bulk_query

arxiv = get_arxiv_collection()

def update_ES_from_arxiv():
    es = get_es_conn()
    _QUERY = get_newly_added_query()

    # _newly_cursor = arxiv.find(_QUERY,limit = 500)
    _newly_cursor = arxiv.find(_QUERY).batch_size(2000) #set baatch_size, the cursor will get 500 each time access the mongo

    #maintain the ids and the field we needed
    _newly_ids = []
    _newly_records = []
    for record in _newly_cursor:
        _newly_ids.append(record['_id'])
        _newly_records.append(record)
        if len(_newly_records) == 2000:
            # insert into ES
            bulk_q = generate_bulk_query(_newly_records,'arxiv')
            es.bulk(bulk_q)
            #update the mongo mark
            _filter_query,_update_query = mark_added_query(_newly_ids)
            arxiv.update_many(_filter_query,_update_query)
            _newly_records=[]
            _newly_ids = []    
            print('insert 2000 record.')        
    else:
        bulk_q = generate_bulk_query(_newly_records,'arxiv')
        if bulk_q:
            es.bulk(bulk_q)
            _filter_query,_update_query = mark_added_query(_newly_ids)
            arxiv.update_many(_filter_query,_update_query)
            print('insert {} record.'.format(len(_newly_records)))
            
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
    update_ES_from_arxiv()        