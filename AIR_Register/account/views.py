from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
#from rest_framework.decorators import api_view
from djongo.models import IntegerField,CharField
from django.views.decorators.csrf import csrf_exempt,csrf_protect

from .models import UserProfile,UserInfo,StringField, ActionLog
from .models import Interests
import json
import bson
import sys
import random
from django.contrib.sessions.models import Session

# import djongo
sys.path.append("../")
from air_ES.query_result import get_rough_query_result

SESSION_KEY = '_auth_user_id'
BACKEND_SESSION_KEY = '_auth_user_backend'
HASH_SESSION_KEY = '_auth_user_hash'
REDIRECT_FIELD_NAME = 'next'

# generate json response for front end
def gen_json_response(session_id,status='success', message="success",data={},):
    res = {
    "status": status,
    "message": message,
    "data": data,
    "session_id":session_id
    }
    return JsonResponse(res)

# record new user's username and password
class RegisterView(View):

    def get(self,request):
        # session_id=request.session.session_key
        return gen_json_response(status='error',message='No get for this page.')
    
    def post(self,request):
        # received_data = json.loads(request.body.decode('utf-8'))
        #use request.body to accommodate front end's axios
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # body = request.POST
        print(body)
        print('!!!!!!!!!!!!')
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
        degree='No degree'

        # print(d1)
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
    
    def get(self,request):
        return gen_json_response(status='error',message='No get for this page.')
    
    def post(self,request):
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
        
        degree = body['degree']

        interests_insert=[]
        # interests_raw = json.loads(interests_raw)
        for x in interests_raw:
            key,value = next(iter(x.items()))
            interests_insert.append(Interests(domain=key,weight=value))

        # debug
        
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
    # template_name = 'account/login.html'
    
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
            uid = user.pk # todo: need tests
            request.session['uid'] = uid
            request.session['test'] = 'hbnb'
        
            print(request.session['uid'])
            print(request.session.keys())
            if not request.session.session_key:
                request.session.save()
            session_id =request.session.session_key
            print(request.user)
            # uid = User.objects.get(username=username).pk
            
            # expected interests from front end:
            # "'interests':[
            #     [{'CV':1.2},{'CV object detection':0.8},{'CV SLAM':0.4}],
            #     [{'NLP':1.3},{'NLP object detection':0.7}，{'NLP SLAM':0.8}]
            # ]"
            print(uid)
            # todo: if speed is too slow, we can redesign the models.py for database
            # reformat input for query 
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
            query_text = [[x.domain, x.weight] for x in interests_raw.interests]
            # query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
            
            # Get recommended papers
            # expected input: [("CV",1.0),("nlp",10.0)]
            # query_text = [("机器学习",10.0),("nlp",10.0)]
            # paper_list = get_rough_query_result(query_text,index='news',fields=[('content',4),('title',10)])
            paper_list = get_rough_query_result(query_text)
            
            # paper_list = [[x.domain, x.weight] for x in interests_raw.interests]
            # print(paper_list[0][1])

            # {'uid':123,'username':'kaizige','degree':'master','interests':[ ['CV',1.2],['object detection,0.8],['slam',0.4],['NLP',1.3],['word embedding',0.7]],‘collections’:[{‘type’:‘arxiv’(or ‘news’,‘github’),type对应的字段},…]}

            data = {"uid":uid,"username":username,"degree":degree,"interests":query_text,"collections":total_collections,"paper_list":paper_list[0]}
            # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
            print(request.session['uid'])
            request.session.modified = True

            response = gen_json_response(session_id,status="success",message="Login success!",data=data)
            # response.set_cookie('session_id','8bnncdah79b55wn2gnz0jh3bah3937bf')
            response.set_cookie('my_cookie','cookie value')
            response.set_cookie('my_cookie2','cookie value2')
            response.set_cookie('session_id',session_id)
            
            request.session['test2'] = 'hbnb'
            request.session.modified = True
            return response


        else:
            return gen_json_response(status='error',message='Wrong username or password!')

        # return HttpResponseRedirect("/account/login")

@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
class CollectView(View):
    def get(self,request):
        body_unicode = request.body.decode('utf-8')
        
        print(body_unicode)
        return gen_json_response(status="successs",message="Return your get.",data=body_unicode)

    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        print(body)
        uid = body['uid']
        iid = body['data']['iid']
        # iid = bson.ObjectId(body['iid'])
        item_type = body['data']['type']
        user_profile = UserProfile.objects.get(uid=uid)
        if item_type == 'arxiv':
            print(type(iid))
            # temp = CharField('sadsdd')
            print(type(user_profile.paper_collections))
            user_profile.paper_collections.append(StringField(text=iid))
            # UserProfile.objects.filter(uid=uid).update(paper_collections=[CharField(iid)]) 
            print(user_profile.paper_collections[0])
            user_profile.save()
        elif item_type == 'news':
            user_profile.news_collections.append(StringField(text=iid))
            user_profile.save()
        elif item_type == 'github':
            user_profile.github_collections.append(StringField(text=iid))
            user_profile.save()
        else :
            return gen_json_response(status="error",message="Wrong type for collection!")
        return gen_json_response(status="successs",message="Collect success.")

# @method_decorator(login_required, name='dispatch')
class FeedsView(View):
    # template_name = 'account/login.html'
    
    def get(self,request):
        # session_id =request.session.session_key
        return gen_json_response(status='error',message='No get for this page.kiddding?')

    def post(self,request):
        print("$$$$$$$$$$$$$$$$$$$$$$$")
        print(request.COOKIES.keys())
        session_id =request.COOKIES['session_id']
        sess = Session.objects.get(pk=session_id)
        print(sess.session_data)
        print(sess.get_decoded())

        
        print(request.session.keys())
        # for key, value in sess.items():
        #     print('{} => {}'.format(key, value))
        # request.session['test']='dddd'
        print(sess.session_key)
        # if not request.session.session_key:
        #     request.session.save()
        # print(request.session.session_key)
        # print(request.session[SESSION_KEY])
        # print(request.session[BACKEND_SESSION_KEY])
        # print(request.session[HASH_SESSION_KEY])
        print("@@@@@@@@@@@@@")
        sess_data = sess.get_decoded()
        hello=type(sess_data)
        print(hello)
        print(sess_data['test'])
        body = json.loads(request.body.decode('utf-8'))
        uid = body["uid"]
        print(uid)
        try:
            if sess_data["uid"] == uid:
                print('only for login')
        except KeyError:
            print("why!!!")
            return gen_json_response(session_id,status='error',message='Please login first!')
        # Expected Input
        # [{"uid":213,"iid":"12dwdaswas22","action":1,"start_time":,"end_time":},...]
        
        # feedback=body["data"]["feedback"]
        print(uid)
        # todo: if speed is too slow, we can redesign the models.py for database
        # reformat input for query 
        # for item in feedback:
        #     action_log = ActionLog(uid=uid,iid=item['iid'],action=item['action'],start_time=item['start_time'],end_time=['end_time'] )
        #     action_log.save()
        # print("------------------")
        try:
            interests_raw = UserProfile.objects.get(uid=uid)
            print(interests_raw)
        except:
            return gen_json_response(status='error',message='Please login first!')
        print(interests_raw)
        # interests = json.loads()
        # mytuple = next(iter(interests[0][0].items()))
        query_text = [[x.domain, x.weight] for x in interests_raw.interests]
        # query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
        
        # Get recommended papers
        # expected input: [("CV",1.0),("nlp",10.0)]
        # query_text = [("机器学习",10.0),("nlp",10.0)]
        # paper_list = get_rough_query_result(query_text,index='news',fields=[('content',4),('title',10)])
        # paper_list = get_rough_query_result(query_text)
        paper_list = [['ooooooo']]
        # paper_list = [[x.domain, x.weight] for x in interests_raw.interests]
        
        random.shuffle(paper_list[0]) # just for testing interface
        print(paper_list[0][1])
        data = {"uid":uid,"paper_list":paper_list[0]}
        # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
        return gen_json_response(session_id,status="success",message="Send feeds success!",data=data)

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    pass

# @method_decorator(login_required, name='dispatch')
class TrendingView(View):
    def get(self,request):
        body = json.loads(request.body.decode('utf-8'))
        uid = body['uid']
        iid = body['iid']
        start_time = body['start_time']
        end_time = body['end_time']
        
        data = {"uid":uid,"iid":iid,"start_time" : start_time,"end_time":end_time}
        # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
        return gen_json_response(status="success",message="Search success!",data=data)
    

    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        print("############")
        print(body)
        uid = body['uid']
        iid = body['iid']
        start_time = body['start_time']
        end_time = body['end_time']
        
        data = {"uid":uid,"iid":iid,"start_time" : start_time,"end_time":end_time}
        # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
        return gen_json_response(status="success",message="Search success!",data=data)
    
    
@method_decorator(login_required, name='dispatch')
class SubscribeView(View):
    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        uid = body['uid']
        interests_raw = body['interests']
        uid = body['uid']

        interests_insert=[]
        # interests_raw = json.loads(interests_raw)
        user_profile = UserProfile.objects.get(uid=uid)
        for x in interests_raw:
            key,value = next(iter(x.items()))
            user_profile.interests.append(Interests(domain=key,weight=value))

        print("@@@@@@@@@@@@@")
        user_profile.save()

        print('save success.')
        return gen_json_response(status="success",message="Subscribe interests success!")

class SearchView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        body = json.loads(request.body.decode('utf-8'))
        uid = body['uid']
        query_raw = body['data']['keywords']
        query_text = [[x, 1.0] for x in query_raw]

        paper_list = get_rough_query_result(query_text)
        
        print(paper_list[0][1])
        data = {"uid":uid,"paper_list":paper_list[0]}
        # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
        return gen_json_response(status="success",message="Search success!",data=data)

