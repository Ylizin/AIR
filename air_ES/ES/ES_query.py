from .ES_connector import get_es_conn
from .QUERY_DICT import get_weighted_query,get_msearch_query,TYPE_FIELDS_MAP
import logging
# logging.basicConfig(level=logging.DEBUG)

def query_text(text:list , fields:list=None, index=['arxiv']):
    '''do query in es, the index param figures the index we gonna search
    
    Arguments:
        text {list of str,weighted} -- the list of string to be searched, and the score they correspond
        fields {list of str,weighted} -- like text above,
    Keyword Arguments:
        index list of {str} 
    '''
    
    _m_query = []
    for i in index:
        _fields = []
        if i not in fields:
            # if index not in fields
            _fields = TYPE_FIELDS_MAP[i]
            _fields = filter(lambda x: not x == 'id',_fields)
            _fields = [(field,1) for field in _fields]
        else:
            _fields = fields[i]
        fields_text_w = [(f[0],text,f[1]) for f in _fields]
        _query = get_weighted_query(fields_text_w)
        _m_query += get_msearch_query(_query,[i],size = 200)
    logging.debug(_m_query)
    if index:
        try:
            res = get_es_conn().msearch(_m_query)['responses']
            # res = get_es_conn().search(index=index,body = _query,size=200)['hits']['hits'] # size is the num of returned docs
        except Exception as e:
            logging.error(e)
            return 'Inner ElasticSearch error.'
    else:
        raise Exception('Index shouldnt be None')
    logging.debug([x['_score'] for x in res[0]['hits']['hits']])
    _records ={}
    _scores = {}
    for i,record in zip(index,res):
        hits = record['hits']['hits']

        _records[i]=[x['_source'] for x in hits]
        _scores[i]=[x['_score'] for x in hits]
    return _records,_scores
    