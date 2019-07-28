from django.http import JsonResponse
from .ES.ES_query import query_text
from .ES.QUERY_DICT import *
from .ES.ES_connector import *

def get_user_tags(user_id):
    user = get_user_collection()
    _query = get_user_tags_query(user_id)
    user_record = user.findOne(_query)


def get_rough_query_result(request,text='Data'):
    arxiv = get_arxiv_collection()
    _text_abs_url = query_text(text)
    titles = []
    for t in _text_abs_url:
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

