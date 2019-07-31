from django.http import JsonResponse
from .ES.ES_query import query_text
from .ES.QUERY_DICT import *
from .ES.ES_connector import *
from airs.rsfunction import get_rs_result

def get_user_tags(user_id):
    if not user_id:
        return None,None,None
    user = get_user_collection()
    _query = get_user_tags_query(user_id)
    user_record = user.find_one(_query)
    if not user_record :
        return None,None,None
    # tag_0 = user_record['initial_tag_0']
    interests = user_record['interests']
    text_w = [(di['domain'],di['weight']) for di in interests]
    return text_w,user_record

def get_rough_query_result(text,index='arxiv',fields=None):
    '''
        we can get the rough search by this method, by passing three param
    '''
    collection = get_collection(index)
    # this is for test case
    if not fields:
        fields = [('abstract',4),('title',10)]

    _search_res,_scores = query_text(text,fields=fields,index=index)
    ids = list(map(lambda x: x['id'],_search_res))
    _q = get_record_info_query(ids)
    result = list(collection.find(_q,projection={'_id':False,'updated':False})[:20])
    for i in result:
        result['type']=index
    return result,_scores

def get_acc_query_result(user_info,rough_info):
    '''this function pass the user_vec and the result of rough seach to the accurate search
    
    Arguments:
        user_vec {[type]} -- [description]
    '''
    return get_rs_result(rough_info[0],rough_info[1],user_info)
