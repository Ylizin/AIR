from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.sessions.models import Session
# from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt,csrf_protect
# import django.contrib.sessions.middleware.SessionMiddleware
from .models import UserProfile,UserInfo,StringField, ActionLog, Interests

import json
import bson
import sys
import random
import time
import datetime

sys.path.append("../")
from air_ES.query_result import get_rough_query_result,get_acc_query_result
from airs import rsfunction
from utils import gen_json_response,get_session_data,action_record_to_dict

USE_ACC_QUERY = False
# generate json response for front end
# record new user's username and password
class RegisterView(View):
    '''Only accept post request with username and password for register
    '''
    def get(self,request):
        # session_id=request.session.session_key
        return gen_json_response(status='error',message='No get for this page.')
    
    def post(self,request):
        '''Args:
            request(
            username: string
            password: string)
           Returns:
            success status
            error status when duplication detected
        '''
        #use request.body to accommodate front end's axios
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # body = request.POST
        print(body)
        username = body['username']
        password = body['password']
        
        #judge if the username is duplicated
        is_duplicated = User.objects.filter(username=username)
        print('############')
        if is_duplicated:
            return gen_json_response(status='error',message='Duplicate username!')
        print('############')
        # initial a user object
        user = User.objects.create_user(
            username=username,
            # email=form.cleaned_data['email'], #todo: add email verification
            password=password,
        )
        # initial user profile
        user_info = UserInfo(user=user)
        # write to db
        user_info.save()
        # get user id
        uid = user.pk
        print('!!!!!!!!!!!!')
        print(uid)
        print('save success.')
        data ={'uid':uid}
        return gen_json_response(status='success',message='Register success!',data=data)

# record new user's interests and degree
class RegisterInterestsView(View):
    '''collect user interests/degree when registration
    '''
    def get(self,request):
        return gen_json_response(status='error',message='No get for this page.')
    
    def post(self,request):
        '''Args:
            interests:
            password: string
           Returns:
            success
            error status when duplication detected
        '''
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        uid = body['uid']
        interests_raw = body['interests']
        # if interests_raw is None:
        # interests_raw = json.loads('[{"CV":1.22}]')
        # interests_insert=[]
        # for x in interests_raw:
        #     key,value = next(iter(x.items()))
        #     interests_insert.append([key,value])
        print(body)
        degree = body['degree']
        print("*******************")
        print(interests_raw)
        interests_insert=[]
        # interests_raw = json.loads(interests_raw)
        total_weight = 0.0
        # nomarlize weigt of each interest
        length = len(interests_raw)
        print(total_weight)
        for x in interests_raw:
            domain, father = list(x.keys())[0],x['father']
            interests_insert.append(Interests(domain=domain,weight=1/length,father=father))
        
        # method 1 to update
        # user = UserProfile.objects.filter(user_id=uid).update(interests=interests_insert,degree=degree)
 
        print("@@@@@@@@@@@@@")
        # method 2 to update
        user_profile = UserProfile(
            uid = uid,#unique=True,primary_key = True
            degree = degree,
            interests = interests_insert,
            paper_collections=[],
            news_collections=[],
            github_collections=[]
                )
        # write to db
        user_profile.save()

        print('save success.')
        return gen_json_response(status="success",message="Register interests success!")


class LoginView(View):

    def get(self,request):
        # session_id=request.session.session_key

        return gen_json_response(status='error',message='No get for this page.kiddding?')
    
    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        username = body["username"]
        password = body["password"]
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            uid = user.pk 
            # add login info into session
            request.session['uid'] = uid
            request.session['test'] = 'hbnb'

            # get session id 
            print(request.session['uid'])
            if not request.session.session_key:
                request.session.save()
            session_id =request.session.session_key

            # expected interests from front end:
            # "'interests':[
            #     [{'CV':1.2},{'CV object detection':0.8},{'CV SLAM':0.4}],
            #     [{'NLP':1.3},{'NLP object detection':0.7}，{'NLP SLAM':0.8}]
            # ]"
            print(uid)
            print("------------------")
            try:
                interests_raw = UserProfile.objects.get(uid=uid)
            except:
                return gen_json_response(session_id,status='error',message='Wrong username or password!')
            # print(interests_raw)
            degree = interests_raw.degree
            paper_collections = interests_raw.paper_collections
            news_collections = interests_raw.news_collections
            github_collections = interests_raw.github_collections
            total_collections = []
            total_collections.append([ str(item) for item in paper_collections])
            total_collections.append([str(item) for item in news_collections])
            total_collections.append([ str(item) for item in github_collections])
            print("------------------")
            print("------------------")
            print("------------------")
            print(total_collections)
            query_text = [[x.domain, x.weight] for x in interests_raw.interests]
            
            # Get recommended papers
            # expected input: [("CV",1.0),("nlp",10.0)]
            # query_text = [("机器学习",10.0),("nlp",10.0)]
            # paper_list = get_rough_query_result(query_text,index='news',fields=[('content',4),('title',10)])
        #     paper_info_score,_ = get_rough_query_result(query_text,index='arxiv')
        # # paper_info = []
        #     news_info_score,_ = get_rough_query_result(query_text,index = 'news')
        #     github_info_score,_ = get_rough_query_result(query_text,index = 'github')
            paper_info_score = get_rough_query_result(query_text,index='arxiv')
        # paper_info = []
            news_info_score = get_rough_query_result(query_text,index = 'news')
            github_info_score = get_rough_query_result(query_text,index = 'github')

            try:
                use_info = dict(interests_raw)
                print(use_info)
            except:
                use_info = []
                print("user info can not be directly changed to dict.")

            print('################################')
            paper_info = get_acc_query_result(use_info,paper_info_score,index='arxiv')
            print('################################')
            news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
            print('################################')
            github_info = get_acc_query_result(use_info,github_info_score,index = 'github') 
            # paper_info = paper_info_score
            # news_info = news_info_score
            # github_info = github_info_score
            paper_list = paper_info + news_info +github_info      
            
            # {'uid':123,'username':'kaizige','degree':'master','interests':[ ['CV',1.2],['object detection,0.8],['slam',0.4],['NLP',1.3],['word embedding',0.7]],‘collections’:[{‘type’:‘arxiv’(or ‘news’,‘github’),type对应的字段},…]}
            # paper_list = paper_info+news_info+github_info
            random.shuffle(paper_list) 
                 
            return_data = paper_list[0:10]

            t = int(round(time.time()* 1000))
            for item in return_data:
                action_record = ActionLog(uid=uid,fid=item['id'],action=0,start_time=t,end_time=0)
                
                action_record.save()
                # action_record = {'uid':uid,'fid':item['fid'],'action':0,'start_time':t,'end_time':0}

            data = {"uid":uid,"username":username,"degree":degree,"interests":query_text,"collections":total_collections,"paper_list":return_data}
            # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
            print(request.session['uid'])
            request.session.modified = True

            response = gen_json_response(session_id,status="success",message="Login success!",data=data)
            # add cookie
            response.set_cookie('session_id',session_id)
            
            return response


        else:
            return gen_json_response(status='error',message='Wrong username or password!')



class LogoutView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        logout(request)
        print('log out ..............')
        return gen_json_response(status="success",message="Logout success!")
        
    def post(self,request):
        logout(request)
        print('log out ..............')
        return gen_json_response(status="success",message="Logout success!")



# class CollectView(View):
#     def get(self,request):
#         body_unicode = request.body.decode('utf-8')
        
#         print(body_unicode)
#         return gen_json_response(status="successs",message="Return your get.",data=body_unicode)

#     def post(self,request):
#         body = json.loads(request.body.decode('utf-8'))
#         print(body)
#         uid = body['uid']
#         fid = body['data']['id']
#         # fid = bson.ObjectId(body['fid'])
#         print(body['data'])
#         item_type = body['data']['type']
#         user_profile = UserProfile.objects.get(uid=uid)
#         # action=3 means this is a collection action
#         action_record = ActionLog(uid=uid,fid=fid,action=3,start_time=body['start_time'],end_time=0)
#         action_record.save()
        
#         if USE_ACC_QUERY:
#             rsfunction.update_interests(action_record_to_dict(action_record))

#         if item_type == 'arxiv':
#             print(type(fid))
#             # temp = CharField('sadsdd')
#             print(type(user_profile.paper_collections))
#             user_profile.paper_collections.append(StringField(text=fid))
#             # UserProfile.objects.filter(uid=uid).update(paper_collections=[CharField(fid)]) 
#             print(user_profile.paper_collections[0])
#             user_profile.save()
#         elif item_type == 'news':
#             user_profile.news_collections.append(StringField(text=fid))
#             user_profile.save()
#         elif item_type == 'github':
#             user_profile.github_collections.append(StringField(text=fid))
#             user_profile.save()
#         else :
#             return gen_json_response(status="error",message="Wrong type for collection!")
#         return gen_json_response(status="successs",message="Collect success.")

# # @method_decorator(login_required, name='dispatch')
# class FeedsView(View):
    
#     def get(self,request):
#         # session_id =request.session.session_key
#         return gen_json_response(status='error',message='No get for this page.kiddding?')

#     def post(self,request):
#         # print(request.COOKIES.keys())
#         try :
#             session_id =request.COOKIES['session_id']
#         except KeyError:
#             return gen_json_response(session_id,status='error',message='Your cookie is lost! Please login again!')

#         print("sid in request in feeds:"+str(request.COOKIES['session_id']))
#         sess = Session.objects.get(pk=session_id)
#         # print(sess.get_decoded())
#         if sess is None:
#             return gen_json_response(session_id,status='error',message='Please login first!')
#         # if not request.session.session_key:
#         #     request.session.save()

#         sess_data = get_session_data(request)
 
#         print(sess_data['test'])
#         body = json.loads(request.body.decode('utf-8'))
#         uid = body["uid"]
#         if uid is None or uid != sess_data["uid"]:
#             return gen_json_response(session_id,status='error',message='Please login first!')

#         print(uid)
#         try:
#             if sess_data["uid"] == uid:
#                 print('only for login')
#         except KeyError:
#             print("why!!!")
#             return gen_json_response(session_id,status='error',message='Please login first!')
#         # Expected Input
#         # [{"uid":213,"fid":"12dwdaswas22","action":1,"start_time":,"end_time":},...]
#         try:
#             interests_raw = UserProfile.objects.get(uid=uid)
#             print(interests_raw)
#         except:
#             return gen_json_response(status='error',message='Please login first!')
#         print(interests_raw)
#         # interests = json.loads()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
#         query_text = [[x.domain, x.weight] for x in interests_raw.interests]
#         # query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
        
#         # rough query result
         
#         paper_info_score = get_rough_query_result(query_text,index='arxiv')
#         # paper_info = []
#         news_info_score = get_rough_query_result(query_text,index = 'news')
#         github_info_score = get_rough_query_result(query_text,index = 'github')
        
#         try:
#             use_info = dict(interests_raw)
#             print(use_info)
#         except:
#             use_info = []
#             print("user info can not be directly changed to dict.")
#         paper_info = get_acc_query_result(use_info,paper_info_score,index='arxiv')
#         news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
#         github_info = get_acc_query_result(use_info,github_info_score,index = 'github')
#         # paper_info_score,_ = get_rough_query_result(query_text,index='arxiv')
#         # news_info_score,_ = get_rough_query_result(query_text,index = 'news')
#         # github_info_score,_ = get_rough_query_result(query_text,index = 'github')
        
#         print('################################')

#         # paper_info = []#get_acc_query_result(use_info,paper_info_score,index='arxiv')
#         # print('################################')
#         # news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
#         # print('################################')
#         # github_info = get_acc_query_result(use_info,github_info_score,index = 'github')
#         # paper_info = paper_info_score
#         # news_info = news_info_score
#         # github_info = github_info_score
#         paper_list = paper_info + news_info + github_info      
#         random.shuffle(paper_list) # just for testing interface
#         return_data = paper_list[0:10]
#         print(return_data[0])
#         for x in return_data:
#             x["fid"] = x.pop("id")
#         t = int(round(time.time()* 1000))
#         for item in return_data:
#             action_record = ActionLog(uid=uid,fid=item['fid'],action=0,start_time=t,end_time=0)
#             action_record.save()
#             # action_record = {'uid':uid,'fid':item['id'],'action':0,'start_time':t,'end_time':0}
#         data = {"uid":uid,"paper_list":return_data}
#         return gen_json_response(session_id,status="success",message="Send feeds success!",data=data)



# class TrendingView(View):
#     def get(self,request):
#         body = json.loads(request.body.decode('utf-8'))
#         uid = body['uid']
#         fid = body['fid']
#         start_time = body['start_time']
#         end_time = body['end_time']
        
#         data = {"uid":uid,"fid":fid,"start_time" : start_time,"end_time":end_time}
#         return gen_json_response(status="success",message="Search success!",data=data)
    

#     def post(self,request):
#         body = json.loads(request.body.decode('utf-8'))
#         print("############")
#         print(body)
#         uid = body['uid']
#         fid = body['fid']
#         start_time = body['start_time']
#         end_time = body['end_time']
        
#         data = {"uid":uid,"fid":fid,"start_time" : start_time,"end_time":end_time}
#         return gen_json_response(status="success",message="Search success!",data=data)
    
    
# class SubscribeView(View):
#     def post(self,request):
#         body = json.loads(request.body.decode('utf-8'))
#         uid = body['uid']
#         interests_raw = body['interests']
#         uid = body['uid']

#         user_profile = UserProfile.objects.get(uid=uid)
#         for x in interests_raw:
#             key,value = next(iter(x.items()))
#             user_profile.interests.append(Interests(domain=key,weight=value))

#         print("@@@@@@@@@@@@@")
#         user_profile.save()

#         print('save success.')
#         return gen_json_response(status="success",message="Subscribe interests success!")

# class SearchView(View):
#     def post(self,request):
#         body = json.loads(request.body.decode('utf-8'))
#         print(body)
#         # uid = body['uid']
#         # print("search uid:"+str(uid))
#         keywords = body['keywords']
#         if not keywords:
#             return JsonResponse({'message':'Nothing to search.','flag':0})
#         text_w = [(keywords,1)]
#         # text_w = [(word,1) for word in keywords]
#         paper_info = get_rough_query_result(text_w,index='arxiv')
#         news_info = get_rough_query_result(text_w,index = 'news')
#         github_info = get_rough_query_result(text_w,index = 'github')
#         paper_list = paper_info+news_info+github_info
#         # texts['texts'] = recommends
#         # return JsonResponse(texts)

#         # query_text = [[x, 1.0] for x in keywords.split(" ")]
#         # print("search text:"+str(query_text))
#         # paper_list = get_rough_query_result(query_text)
        
#         # print(paper_list[0][1])
#         data = {"paper_list":paper_list[0][0:100]}
#         return gen_json_response(status="success",message="Search success!",data=data)


# class ClickView(View):
#     def post(self,request):
#         body = json.loads(request.body.decode('utf-8'))
#         print(body)

#         action_record = ActionLog(uid=body['uid'],fid=body['fid'],action=body['action'],start_time=body['start_time'],end_time=0)
#         action_record.save()

#         if USE_ACC_QUERY:
#             rsfunction.update_interests(action_record_to_dict(action_record))
#         data = {}
#         return gen_json_response(status="success",message="Search success!",data=data)
