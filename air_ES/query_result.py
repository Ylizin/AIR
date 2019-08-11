from django.http import JsonResponse
from .ES.ES_query import query_text
from .ES.QUERY_DICT import *
from .ES.ES_connector import *
from airs.rsfunction import get_rs_result
import pickle 
en_to_cn_dict = pickle.load(open('./en_to_cn.pkl','rb'))

def get_user_tags(uid):
    if not uid:
        return None,None
    user = get_user_collection()
    _query = get_user_tags_query(uid)
    user_record = user.find_one(_query)
    if not user_record :
        return None,None
    # tag_0 = user_record['initial_tag_0']
    interests = user_record['interests']
    text_w = [(di['domain'],di['weight']) for di in interests]
    return text_w,user_record

def get_rough_query_result(text,index=['arxiv'],fields=None):
    '''
        we can get the rough search by this method, by passing three param
        the text is a list of tuples of (tag,weight)
        the index is the list of index in ES
        the fields is the (field,weight) to be searched in ES
        if the fields is None then this method will search each field except 'id' with weigth 1

        it returns a list of records, corresponding to the order passed in 
    '''
    # get a copy of the text since it will be sent to the frontend
    _text = text.copy()
    if 'news' in index:
        # convert en to cn if tag in en_to_cn_dict and add it into 
        _text += [(en_to_cn_dict[tag],w) for tag,w in _text if tag in en_to_cn_dict]
        
    # the result is a dict of {key: list of result},{key: list of scores}
    search_res,scores = query_text(_text,fields=fields,index=index)
    
    _result_scores = {}
    for i in index:    
        collection = get_collection(i)
        ids = list(map(lambda x: x['id'],search_res[i]))
        _q = get_record_info_query(ids)
        result = list(collection.find(_q,projection={'updated':False}))
        # add the type info to each record
        # the '_id' is the id in mongodb, here parse it to a str then send it through a json in 'id'
        _ = [d.update({'type':i}) for d in result]
        _ = [d.update({'id':str(d.pop('_id'))}) for d in result]
        _result_scores[i] = (result,scores[i])
    return _result_scores

def get_acc_query_result(user_info,rough_info,index):
    '''this function pass the user_vec and the result of rough seach to the accurate search
    Arguments:
        user_vec {[type]} -- [description]
    '''
    # if not user_info or not rough_info:
        # return [{'error':1,'message':'No result found in index: '+index}]
    result = get_rs_result(rough_info[0],rough_info[1],user_info,index)
    return result


def get_feeds_info(f_ids,index = 'arxiv'):
    '''
        get paper/news/github info from ids
        return a list
    '''
    collection = get_collection(index)
    _q = get_record_info_query(f_ids)

    collection_records = list(collection.find(_q,projection={'updated':False}))
    _ = [d.update({'type':index}) for d in collection_records]
    _ = [d.update({'fid':str(d.pop('_id'))}) for d in collection_records]
    return  collection_records
