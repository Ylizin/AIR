from django.http import JsonResponse
from .ES.ES_query import query_text
from .ES.QUERY_DICT import *
from .ES.ES_connector import *
from airs.rsfunction import get_rs_result


def get_user_tags(uid):
    if not uid:
        return None,None,None
    user = get_user_collection()
    _query = get_user_tags_query(uid)
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
        the text is a list of tuples of (tag,weight)
        the index is the index in ES
        the fields is the (field,weight) to be searched in ES
        if the fields is None then this method will search each field except 'id' with weigth 1
        
    '''
    collection = get_collection(index)
    # this is for test case
    if not fields:
        fields = TYPE_FIELDS_MAP[index]
        fields = filter(lambda x: not x == 'id',fields)
        fields = [(field,1) for field in fields]

    _search_res,_scores = query_text(text,fields=fields,index=index)
    ids = list(map(lambda x: x['id'],_search_res))
    _q = get_record_info_query(ids)
    result = list(collection.find(_q,projection={'updated':False})[:20])
    # add the type info to each record
    # the '_id' is the id in mongodb, here parse it to a str then send it through a json in 'id'
    _ = [d.update({'type':index}) for d in result]
    _ = [d.update({'id':str(d.pop('_id'))}) for d in result]

    return result,_scores

def get_acc_query_result(user_info,rough_info):
    '''this function pass the user_vec and the result of rough seach to the accurate search
    Arguments:
        user_vec {[type]} -- [description]
    '''
    result = get_rs_result(rough_info[0],rough_info[1],user_info)
    return result
