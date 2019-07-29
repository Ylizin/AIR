from django.http import JsonResponse
from .ES.ES_query import query_text
from .ES.QUERY_DICT import *
from .ES.ES_connector import *

def get_user_tags(user_id):
    if not user_id:
        return None,None
    user = get_user_collection()
    _query = get_user_tags_query(user_id)
    user_record = user.find_one(_query)
    if not user_record :
        return None,None
    tag_0 = user_record['initial_tag_0']
    tag_1 = user_record['initial_tag_1']
    return tag_0,tag_1

def get_rough_query_result(text,_index='arxiv',fields=None):
    '''we can get the rough search by this method, by passing three param
    
    Keyword Arguments:
        text {list((str),weight)} -- [description] (default: {'Data'})
        _index {str} -- [description] (default: {'arxiv'})
        fields {[type]} -- [description] (default: {None})
    
    Returns:
        [type] -- [description]
    '''
    arxiv = get_arxiv_collection()
    if not fields:
        fields = [('abstract',4),('title',10)]
    _search_res,_ = query_text(text,fields=fields,_index=_index)
    titles = []
    for t in _search_res:
        _title = t['title']
        titles.append(_title)
    _q = get_paper_info_query(titles)
    result = arxiv.find(_q)
    return result

def get_acc_query_result(user_info,rough_info):
    '''this function pass the user_vec and the result of rough seach to the accurate search
    
    Arguments:
        user_vec {[type]} -- [description]
    '''
    pass

