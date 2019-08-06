
from django.http import JsonResponse
from django.contrib.sessions.models import Session

def gen_json_response(session_id=0,status='success', message="success",data={},):
    res = {
    "status": status,
    "message": message,
    "data": data,
    "session_id":session_id
    }
    return JsonResponse(res)
def get_session_data(session_id):
    '''Read information from mongodb using request with 'session_id' in cookies
       Args: 
            http request from client
       Returns:
            parsed session data
    '''

    sess = Session.objects.get(pk=session_id)
    return sess.get_decoded()
    
def action_record_to_dict(action_record):
    res = {
        'uid':action_record.uid,
        'fid':action_record.fid,
        'action':action_record.action,
        'start_time':action_record.start_time,
        'end_time':action_record.end_time
    }
    return res
