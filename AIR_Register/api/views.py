from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.sessions.models import Session

from account.models import UserProfile,UserInfo,StringField, ActionLog, Interests

import json
import bson
import sys
import random
import time
import datetime

sys.path.append("../")
from air_ES.query_result import get_rough_query_result,get_acc_query_result,get_feeds_info
from airs import rsfunction
from utils import gen_json_response,get_session_data,action_record_to_dict

USE_ACC_QUERY = True
# generate json response for front end



class CollectView(View):
    '''
    '''
    def get(self,request):
        body_unicode = request.body.decode('utf-8')
        
        print(body_unicode)
        return gen_json_response(status="successs",message="Return your get.",data=body_unicode)

    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        uid = body['uid']
        fid = body['fid']
        # print(body['data'])
        item_type = body['type']
        user_profile = UserProfile.objects.get(uid=uid)
        # action=3 means this is a collection action
        print('############################')
        print(uid)
        print(item_type)
        t = int(round(time.time()* 1000))
        is_favor = body['fav_action']
        if is_favor == 'favor':
            action_record = ActionLog(uid=uid,fid=fid,action=3,start_time=t,end_time=0)
        else:
            action_record = ActionLog(uid=uid,fid=fid,action=-2,start_time=t,end_time=0)
        action_record.save()
        
        if USE_ACC_QUERY:
            rsfunction.update_interests(action_record_to_dict(action_record))

        if item_type == 'arxiv':
            # temp = CharField('sadsdd')
            if is_favor == 'favor':
                temp = StringField(text=fid)
                if temp in user_profile.paper_collections:
                    pass
                else:
                    user_profile.paper_collections.append(StringField(text=fid))
            else:
                print("---------collect-----------")
                print(user_profile.paper_collections)
                temp = StringField(text=fid)
                print('------')
                print(temp)    
                user_profile.paper_collections.remove(temp)
                print(user_profile.paper_collections)
                print("remove success.")
            # UserProfile.objects.filter(uid=uid).update(paper_collections=[CharField(fid)]) 
            # print(user_profile.paper_collections[0])
            user_profile.save()
        elif item_type == 'news':
            user_profile.news_collections.append(StringField(text=fid))
            user_profile.save()
        elif item_type == 'github':
            user_profile.github_collections.append(StringField(text=fid))
            user_profile.save()
        else :
            return gen_json_response(status="error",message="Wrong type for collection!")
        return gen_json_response(status="successs",message="Collect success.")

# @method_decorator(login_required, name='dispatch')
class FeedsView(View):
    
    def get(self,request):
        # session_id =request.session.session_key
        return gen_json_response(status='error',message='No get for this page.kiddding?')

    def post(self,request):
        _start_time = time.perf_counter()
        # print(request.COOKIES.keys())
        try :
            session_id =request.COOKIES['session_id']
            # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            # print(session_id)
        except KeyError:
            return gen_json_response(status='error',message='Your cookie is lost! Please login again!')
        sess = Session.objects.get(pk=session_id) 
        sess_data = sess.get_decoded()# get_session_data(session_id)
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        # print(sess_data)
        # print(sess.get_decoded())
        if sess_data is None:
            return gen_json_response(session_id,status='error',message='Your cookie is lost! Please login again!')

        body = json.loads(request.body.decode('utf-8'))
        uid = body["uid"]
        if uid is None or uid != sess_data["uid"]:
            return gen_json_response(session_id,status='error',message='Please login first!')

        print(uid)
        try:
            if sess_data["uid"] == uid:
                print('only for login')
        except KeyError:
            print("why!!!")
            return gen_json_response(session_id,status='error',message='Please login first!')
        # Expected Input
        # [{"uid":213,"fid":"12dwdaswas22","action":1,"start_time":,"end_time":},...]
        try:
            interests_raw = UserProfile.objects.get(uid=uid)
            # print(interests_raw)
        except:
            return gen_json_response(status='error',message='Please login first!')
        print(interests_raw)
        # interests = json.loads()
        query_text = [[x.domain, x.weight] for x in interests_raw.interests]
        # query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
        
        _start_rough= time.perf_counter()
        # rough query result 
        index = ['arxiv','news','github']
        total_info_score = get_rough_query_result(query_text,index=index)

        paper_info_score = total_info_score['arxiv']
        news_info_score = total_info_score['news']
        github_info_score = total_info_score['github']
        # github_info_score = get_rough_query_result(query_text,index = 'github')

        _end_rough = time.perf_counter()
        print('------------------------rough time-----------')
        print(_end_rough-_start_rough)
        try:
            use_info = uid
            print(use_info)
        except:
            use_info = []
            print("user info can not be directly changed to dict.")
        
        _acc_start = time.perf_counter()
        paper_info = get_acc_query_result(use_info,paper_info_score,index='arxiv')
        news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
        github_info = get_acc_query_result(use_info,github_info_score,index = 'github')
        # paper_info_score,_ = get_rough_query_result(query_text,index='arxiv')
        # news_info_score,_ = get_rough_query_result(query_text,index = 'news')
        # github_info_score,_ = get_rough_query_result(query_text,index = 'github')
        _acc_end = time.perf_counter()
        print('--------------acc time--------------')
        print(_acc_end - _acc_start)
        print('################################')

        # paper_info = []#get_acc_query_result(use_info,paper_info_score,index='arxiv')
        # print('################################')
        # news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
        # print('################################')
        # github_info = get_acc_query_result(use_info,github_info_score,index = 'github')
        # paper_info = paper_info_score
        # news_info = news_info_score
        # github_info = github_info_score
        paper_list = paper_info + news_info + github_info      
        random.shuffle(paper_list) # just for testing interface
        return_data = paper_list[0:10]
        # print(return_data[0])
        for x in return_data:
            x["fid"] = x.pop("id")
        t = int(round(time.time()* 1000))
        for item in return_data:
            action_record = ActionLog(uid=uid,fid=item['fid'],action=0,start_time=t,end_time=0)
            action_record.save()
            # action_record = {'uid':uid,'fid':item['id'],'action':0,'start_time':t,'end_time':0}
        data = {"uid":uid,"paper_list":return_data}
        _end_time = time.perf_counter()
        print('-----------------totoal req time---------------')
        print(_end_time-_start_time)
        return gen_json_response(session_id,status="success",message="Send feeds success!",data=data)



class TrendingView(View):
    def get(self,request):
        body = json.loads(request.body.decode('utf-8'))
        uid = body['uid']
        fid = body['fid']
        start_time = body['start_time']
        end_time = body['end_time']
        
        data = {"uid":uid,"fid":fid,"start_time" : start_time,"end_time":end_time}
        return gen_json_response(status="success",message="Search success!",data=data)
    

    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        print("############")
        print(body)
        uid = body['uid']
        fid = body['fid']
        start_time = body['start_time']
        end_time = body['end_time']
        
        data = {"uid":uid,"fid":fid,"start_time" : start_time,"end_time":end_time}
        return gen_json_response(status="success",message="Search success!",data=data)
    
    
class SubscribeView(View):
    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        uid = body['uid']
        interests_raw = body['interests']
        uid = body['uid']

        user_profile = UserProfile.objects.get(uid=uid)
        for x in interests_raw:
            key,value = next(iter(x.items()))
            user_profile.interests.append(Interests(domain=key,weight=value))

        print("@@@@@@@@@@@@@")
        user_profile.save()

        print('save success.')
        return gen_json_response(status="success",message="Subscribe interests success!")

class SearchView(View):
    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        # uid = body['uid']
        # print("search uid:"+str(uid))
        keywords = body['keywords']
        if not keywords:
            return JsonResponse({'message':'Nothing to search.','flag':0})
        text_w = [(keywords,1)]
        
        # text_w = [(word,1) for word in keywords]
        index = ['arxiv','news','github']
        total_info_score = get_rough_query_result(text_w,index=index)

        # paper_info_score = total_info_score['arxiv']
        # # # paper_info = []
        # news_info_score = total_info_score['news']
        # github_info_score = total_info_score['github']

        # paper_info,_ = get_rough_query_result(text_w,index='arxiv')
        # news_info,_ = get_rough_query_result(text_w,index = 'news')
        # github_info,_ = get_rough_query_result(text_w,index = 'github')
        paper_list = total_info_score[0]#paper_info+news_info+github_info
        # print("-------debug search------------")
        # print(paper_list[0])
        for x in paper_list:
            x["fid"] = x.pop("id")
        random.shuffle(paper_list)
        data = {"paper_list":paper_list[0:50]}
        return gen_json_response(status="success",message="Search success!",data=data)


class ClickView(View):
    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        t = int(round(time.time()* 1000))
        action_record = ActionLog(uid=body['uid'],fid=body['fid'],action=body['action'],start_time=t,end_time=0)
        action_record.save()

        if USE_ACC_QUERY:
            rsfunction.update_interests(action_record_to_dict(action_record))
        data = {}
        return gen_json_response(status="success",message="Search success!",data=data)


class TabView(View):
    
    def get(self,request):
        # session_id =request.session.session_key
        return gen_json_response(status='error',message='No get for this page.kiddding?')

    def post(self,request):
        # print(request.COOKIES.keys())
        
        try :
            session_id =request.COOKIES['session_id']
            # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            # print(session_id)
        except KeyError:
            return gen_json_response(status='error',message='Your cookie is lost! Please login again!')
        sess = Session.objects.get(pk=session_id) 
        sess_data = sess.get_decoded()# get_session_data(session_id)
        # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        # print(sess_data)

        if sess_data is None:
            return gen_json_response(session_id,status='error',message='Your cookie is lost! Please login again!')

        body = json.loads(request.body.decode('utf-8'))
        category = body["category"]
        uid = body["uid"]
        if uid is None or uid != sess_data["uid"]:
            return gen_json_response(session_id,status='error',message='Please login first!')

        print(uid)
        try:
            if sess_data["uid"] == uid:
                print('only for login')
        except KeyError:
            print("why!!!")
            return gen_json_response(session_id,status='error',message='Please login first!')
        # Expected Input
        # [{"uid":213,"fid":"12dwdaswas22","action":1,"start_time":,"end_time":},...]
        try:
            interests_raw = UserProfile.objects.get(uid=uid)
            # print(interests_raw)
        except:
            return gen_json_response(status='error',message='Please login first!')
        # print(interests_raw)
        
        query_text = [[x.domain, x.weight] for x in interests_raw.interests]
        # query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
        index = [category]
        total_info_score = get_rough_query_result(query_text,index=index)

        result_info_score = total_info_score[category]
        
        try:
            use_info = uid
            print(use_info)
        except:
            use_info = []
            print("user info can not be directly changed to dict.")
        result_info = get_acc_query_result(use_info,result_info_score,index=category)
        
        print('################################')    
        random.shuffle(result_info) # just for testing interface
        return_data = result_info[0:10]
        # print(return_data[0])
        for x in return_data:
            x["fid"] = x.pop("id")
        t = int(round(time.time()* 1000))
        for item in return_data:
            action_record = ActionLog(uid=uid,fid=item['fid'],action=0,start_time=t,end_time=0)
            action_record.save()
            # action_record = {'uid':uid,'fid':item['id'],'action':0,'start_time':t,'end_time':0}
        data = {"uid":uid,"paper_list":return_data}
        return gen_json_response(session_id,status="success",message="Send feeds success!",data=data)

