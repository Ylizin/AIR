from .ES_connector import get_es_conn
from .QUERY_DICT import get_weighted_query
import logging
# logging.basicConfig(level=logging.DEBUG)

def query_text(text:list , fields:list=None, _index:str='test-index'):
    '''do query in es, the index param figures the index we gonna search
    
    Arguments:
        text {list of str,weighted} -- the list of string to be searched, and the score they correspond
        fields {list of str,weighted} -- like text above,
    Keyword Arguments:
        index {str} -- [description] (default: {'paper':str})
    '''
    #abstract and title have different weight in scoring
    if not fields:
        fields = [('abstract',4),('title',10)]

    fields_text_w=[]
    for tup in fields:
        fields_text_w.append((tup[0],text,tup[1]))
    _query = get_weighted_query(fields_text_w)
    logging.debug(_query)
    if _index:
        try:
            res = get_es_conn().search(index=_index,body = _query,size=200)['hits']['hits'] # size is the num of returned docs
        except Exception as e:
            logging.error(e)
            return 'Inner ElasticSearch error.'
    else:
        raise Exception('Index shouldnt be None')
    logging.debug([x['_score'] for x in res])
    return [x['_source'] for x in res],[x['_score'] for x in res]
    