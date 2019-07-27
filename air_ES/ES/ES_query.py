from .ES_connector import get_es_conn
from .QUERY_DICT import get_weighted_query
from elasticsearch_dsl import Search
import logging

def query_text(text:str , _index:str='test-index'):
    '''do query in es, the index param figures the index we gonna search
    
    Arguments:
        text {str} -- the string to be searched, it will be tokenized
    
    Keyword Arguments:
        index {str} -- [description] (default: {'paper':str})
    '''
    #abstract and title have different weight in scoring
    _query = get_weighted_query([('abstract',text,4),('title',text,10)])
    if _index:
        try:
            res = get_es_conn().search(index=_index,body = _query,size=200)['hits']['hits'] # size is the num of returned docs
        except Exception as e:
            logging.error(e)
            return 'Inner ElasticSearch error.'
    else:
        raise Exception('Index should be None')
    return [x['_source'] for x in res]
    