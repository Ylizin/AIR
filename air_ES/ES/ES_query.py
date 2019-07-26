from .ES_connector import get_es_conn
from .QUERY_DICT import get_weighted_query
from elasticsearch_dsl import Search

def query_text(text:str,_index:str='test-index'):
    '''do query in es, the index param figures the index we gonna search
    
    Arguments:
        text {str} -- the string to be searched, it will be tokenized
    
    Keyword Arguments:
        index {str} -- [description] (default: {'paper':str})
    '''
    _query = get_weighted_query([('title',text,4),('text',text,'10')])
    if _index:
        res = get_es_conn().search(index=_index,body = _query)['hits']['hits']
    else:
        raise Exception('Index should be None')
    return [x['_source'] for x in res]
    