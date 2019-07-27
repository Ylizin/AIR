from django.http import JsonResponse
from .ES.ES_query import query_text

def get_rough_query_result(request,text='Data'):
    _text_abs_url = query_text(text)
    titles = []
    for t in _text_abs_url:
        _title = t['title']
        titles.append(_title)
    
    return JsonResponse({'texts':query_text(text)})

def get_acc_query_result(user_vec,rough_vec):
    '''this function pass the user_vec and the result of rough seach to the accurate search
    
    Arguments:
        user_vec {[type]} -- [description]
    '''
    pass

