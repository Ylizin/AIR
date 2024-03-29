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
from air_ES.query_result import get_rough_query_result,get_acc_query_result,get_feeds_info
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
        if not request.session.session_key:
            request.session.save()
        request.session['uid'] = uid
        
        request.session.modified = True
        response = gen_json_response(status='success',message='Register success!',data=data)
        session_id =request.session.session_key
        response.set_cookie('session_id',session_id)
        return response


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

        print(body)
        degree = body['degree']
        print("*******************")
        #print(interests_raw)
        interests_insert=[]
        # nomarlize weigt of each interest
        for x in interests_raw:
            domain = x#list(x.keys())[0]
            interests_insert.append(Interests(domain=domain,weight=1,father="hbnb"))
            #interests_insert.append(Interests(domain=domain.lower(),weight=1,father="hbnb"))
        
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
        
        ##############3
        degree = user_profile.degree
        paper_collections = user_profile.paper_collections
        news_collections = user_profile.news_collections
        github_collections = user_profile.github_collections
        total_collections = []
        total_collections.append([ str(item) for item in paper_collections])
        total_collections.append([str(item) for item in news_collections])
        total_collections.append([ str(item) for item in github_collections])
        print("------------------")
        print("------------------")
        print("------------------")
        print(total_collections)
        interests = [[x.domain, x.weight] for x in user_profile.interests]
        _res_interests = [[x[0],x[1]] for x in interests[:100] if x[1]>0]
        query_text = [[x[0],x[1]] for x in interests if x[1] > 0]
        
       
        index = ['arxiv','news','github']
        total_info_score = get_rough_query_result(query_text,index=index)

        paper_info_score = total_info_score['arxiv']
        news_info_score = total_info_score['news']
        github_info_score = total_info_score['github']


        try:
            use_info = uid
            print(use_info)
        except:
            use_info = []
            print("user info can not be directly changed to dict.")

        print('################################')
        paper_info = get_acc_query_result(use_info,paper_info_score,index='arxiv')
        news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
        github_info = get_acc_query_result(use_info,github_info_score,index = 'github') 
        paper_list = paper_info + news_info +github_info      

        random.shuffle(paper_list) 
                
        return_data = paper_list[0:10]

        t = int(round(time.time()* 1000))
        for item in return_data:

            item['fid'] = item.pop('id')
            action_record = ActionLog(uid=uid,fid=item['fid'],action=0,start_time=t,end_time=0)
            
            action_record.save()

        
        data = {"uid":uid,"degree":degree,"interests":_res_interests,"collections":total_collections,"paper_list":return_data}

        #############3


        return gen_json_response(status="success",message="Register interests success!",data=data)


class LoginView(View):

    def get(self,request):
        # session_id=request.session.session_key

        return gen_json_response(status='error',message='No get for this page.kiddding?')
    
    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        username = body["username"]
        password = body["password"]
        #print('hbnb')
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
                user_profile = UserProfile.objects.get(uid=uid)
            except:
                return gen_json_response(session_id,status='error',message='Wrong username or password!')
            # print(interests_raw)
            
            degree = user_profile.degree
            paper_collections = user_profile.paper_collections
            news_collections = user_profile.news_collections
            github_collections = user_profile.github_collections
            total_collections = []
            total_collections.append([ str(item) for item in paper_collections])
            total_collections.append([str(item) for item in news_collections])
            total_collections.append([ str(item) for item in github_collections])
            print("------------------")
            print("------------------")
            print("------------------")
            print(total_collections)
            interests = [[x.domain, x.weight] for x in user_profile.interests]
            query_text = [[x[0], x[1]] for x in interests if x[1] >0]
            _res_interests = [[x[0],x[1]] for x in interests[:100] if x[1]>0]
            # return_interests = [[x.domain, x.weight] for x in user_profile.interests if x.weight >= 1 ]
            
            # Get recommended papers
            # expected input: [("CV",1.0),("nlp",10.0)]
            # query_text = [("机器学习",10.0),("nlp",10.0)]
            # paper_list = get_rough_query_result(query_text,index='news',fields=[('content',4),('title',10)])
            #     paper_info_score,_ = get_rough_query_result(query_text,index='arxiv')
            # # paper_info = []
            #     news_info_score,_ = get_rough_query_result(query_text,index = 'news')
            #     github_info_score,_ = get_rough_query_result(query_text,index = 'github')
            index = ['arxiv','news','github']
            total_info_score = get_rough_query_result(query_text,index=index)

            paper_info_score = total_info_score['arxiv']
            # # # paper_info = []
            news_info_score = total_info_score['news']
            github_info_score = total_info_score['github']

        # paper_info_score = get_rough_query_result(query_text,index='arxiv')
        # paper_info = []
            # news_info_score = get_rough_query_result(query_text,index = 'news')
            # github_info_score = get_rough_query_result(query_text,index = 'github')

            try:
                use_info = uid
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

                item['fid'] = item.pop('id')
                action_record = ActionLog(uid=uid,fid=item['fid'],action=0,start_time=t,end_time=0)
                
                action_record.save()
                # action_record = {'uid':uid,'fid':item['fid'],'action':0,'start_time':t,'end_time':0}
            data = {"uid":uid,"username":username,"degree":degree,"interests":_res_interests,"collections":total_collections,"paper_list":return_data}
            # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
            print('***********debug login')
            #print(data['interests'])
            #print(request.session['uid'])
            request.session.modified = True

            response = gen_json_response(session_id,status="success",message="Login success!",data=data)
            # add cookie
            response.set_cookie('session_id',session_id)
            
            request.session['test2'] = 'hbnb'
            request.session.modified = True
            return response


        else:
            return gen_json_response(status='error',message='Wrong username or password!')



class LogoutView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        
        return gen_json_response(status="success",message="Logout success!")
        
    def post(self,request):
        # print('log out ..............')
        # logout(request)
        # # request
        # try :
        #     session_id =request.COOKIES['session_id']
        #     # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
        #     # print(session_id)
        # except KeyError:
        #     return gen_json_response(status='error',message='Your cookie is lost! Please login again!')
    
        # sess = Session.objects.get(pk=session_id) 
        # print(sess) 
        return gen_json_response(status="success",message="Logout success!")

class CollectionsView(View):

    def post(self,request):
        '''Input: uid, collection_list, 

        '''
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # body = request.POST
        print(body)
        uid = body['uid']
        user_profile = UserProfile.objects.get(uid=uid)
        paper_collections = [ str(item) for item in user_profile.paper_collections]
        news_collections = [ str(item) for item in user_profile.news_collections]
        github_collections = [ str(item) for item in user_profile.github_collections]
        paper_collections_list = get_feeds_info(paper_collections,index='arxiv')
        news_collections_list = get_feeds_info(news_collections,index='news')
        github_collections_list = get_feeds_info(github_collections,index='github')
        res = []
        res.append(paper_collections_list)
        res.append(news_collections_list)
        res.append(github_collections_list)
        # print("-----debug collections view----")
        # print(res)
        return gen_json_response(status='success',data=res)


        
class UpdateInterestsView(View):
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

        print(body)
        degree = body['degree']
        print("*******************")
        #print(interests_raw)
        interests_insert=[]

        for x in interests_raw:
            domain = x
            interests_insert.append(Interests(domain=domain.lower(),weight=1,father="hbnb"))
        
        user_profile = UserProfile.objects.get(uid=uid)
        user_profile.interests = interests_insert
        user_profile.degree = degree
    
        # write to db
        user_profile.save()
        
        paper_collections = user_profile.paper_collections
        news_collections = user_profile.news_collections
        github_collections = user_profile.github_collections
        total_collections = []
        total_collections.append([ str(item) for item in paper_collections])
        total_collections.append([str(item) for item in news_collections])
        total_collections.append([ str(item) for item in github_collections])
        print("------------------")
        print("------------------")
        query_text = [[x.domain, x.weight] for x in user_profile.interests if x.weight > 0]
        
        
        index = ['arxiv','news','github']
        total_info_score = get_rough_query_result(query_text,index=index)

        paper_info_score = total_info_score['arxiv']
        # # # paper_info = []
        news_info_score = total_info_score['news']
        github_info_score = total_info_score['github']

        use_info = uid
        print('################################')
        paper_info = get_acc_query_result(use_info,paper_info_score,index='arxiv')
        print('################################')
        news_info = get_acc_query_result(use_info,news_info_score,index = 'news')
        print('################################')
        github_info = get_acc_query_result(use_info,github_info_score,index = 'github') 

        paper_list = paper_info + news_info +github_info      
        random.shuffle(paper_list) 
                
        return_data = paper_list[0:10]

        t = int(round(time.time()* 1000))
        for item in return_data:

            item['fid'] = item.pop('id')
            action_record = ActionLog(uid=uid,fid=item['fid'],action=0,start_time=t,end_time=0)
            
            action_record.save()
        data = {"uid":uid,"degree":degree,"interests":query_text,"collections":total_collections,"paper_list":return_data}

        # print(request.session['uid'])
        # request.session.modified = True
        print(data["interests"])
        response = gen_json_response(status="success",message="Update interests success!",data=data)

        print('update success.')
        # add cookie
        # response.set_cookie('session_id',session_id)
        
        return response


class UpdateDegreeView(View):
    def get(self,request):
        return gen_json_response(status='error',message='No get for this page.')
    def post(self,request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        uid = body['uid']

        print(body)
        degree = body['degree']

        user_profile = UserProfile.objects.get(uid=uid)
        user_profile.degree = degree
    
        # write to db
        user_profile.save()

        data = {"uid":uid, "degree":degree}

        # print(request.session['uid'])
        # request.session.modified = True
        print(data["degree"])
        response = gen_json_response(status="success",message="Update degree success!",data=data)

        print('update success.')
        # add cookie
        # response.set_cookie('session_id',session_id)
        
        return response
    
