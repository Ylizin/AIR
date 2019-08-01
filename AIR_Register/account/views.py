from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
#from rest_framework.decorators import api_view
from djongo.models import IntegerField,CharField

from .models import UserProfile,UserInfo,StringField
from .models import Interests
import json
import bson
import sys

# import djongo
sys.path.append("../")
from air_ES.query_result import get_rough_query_result

# generate json response for front end
def gen_json_response(status='success', message="success",data={}):
    res = {
    "status": status,
    "message": message,
    "data": data
    }
    return JsonResponse(res)

# record new user's username and password
class RegisterView(View):

    def get(self,request):
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
        print(username)
        print(password)
        # interests = "Nothing"
        # interests = body['interests']
        # interests_raw = body['interests']
        
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
        # interests = 
        # d1 = Interests(domain='asd',weight=2)
        # d2 = Interests(domain='asddd',weight=3)
        # print(d1)
        # Interests(domain='asd',weight=2),Interests(domain='asddd',weight=3)
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
        # print(degree)
        # if interests_raw is None:
        # print(interests_raw[0])
        # print(type(interests_raw[0]))
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
        return gen_json_response(status='error',message='No get for this page.kiddding?')

    def post(self,request):
        body = json.loads(request.body.decode('utf-8'))
        username = body["username"]
        password = body["password"]

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            # uid = User.objects.get(username=username).pk
            uid = user.pk # todo: need tests
            # expected interests from front end:
            # "'interests':[
            #     [{'CV':1.2},{'CV object detection':0.8},{'CV SLAM':0.4}],
            #     [{'NLP':1.3},{'NLP object detection':0.7}，{'NLP SLAM':0.8}]
            # ]"
            print(uid)
            # todo: if speed is too slow, we can redesign the models.py for database
            # reformat input for query 
            print("------------------")
            interests_raw = UserProfile.objects.get(uid=uid)
            print(interests_raw)
            # interests = json.loads()
            # mytuple = next(iter(interests[0][0].items()))
            query_text = [[x.domain, x.weight] for x in interests_raw.interests]
            # query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
            
            # Get recommended papers
            # expected input: [("CV",1.0),("nlp",10.0)]
            query_text = [("机器学习",10.0),("nlp",10.0)]
            # paper_list = get_rough_query_result(query_text,index='news',fields=[('content',4),('title',10)])
            paper_list = get_rough_query_result(query_text)
            
            # paper_list = [[x.domain, x.weight] for x in interests_raw.interests]
            print(paper_list[0][1])
            data = {"uid":uid,"paper_list":paper_list[0]}
            # data = {"status":"success","message":"Login success!","data":{"uid":uid}}
            return gen_json_response(status="success",message="Login success!",data=data)

            # response.set_cookie('username',username,3600)
        else:
            return gen_json_response(status='error',message='Wrong username or password!')

        # return HttpResponseRedirect("/account/login")

class LogoutView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        logout(request)
        print('log out ..............')
        # username = request.POST.get('username')
        # return render(request,'account/login.html', {'message': 'Logout success.'})
        # return HttpResponseRedirect('/account/login')
        return gen_json_response(status="success",message="Logout success!")
        
    def post(self,request):
        logout(request)
        print('log out ..............')
        # return render(request,'account/login.html', {'form': form,'message': 'Logout success.'})
        # return HttpResponseRedirect('/account/login')
        return gen_json_response(status="success",message="Logout success!")

# @method_decorator(login_required, name='dispatch')
class IndexView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        # form = LoginForm(None)
        # return render(request,'account/login.html', {'form': form,'message': 'Logout success.'})
        return render(request, 'account/index.html')
        # return HttpResponseRedirect("account/index.html")
        # return JsonResponse(__get_response_json_dict(data={}))


class FeedsView(View):
    def get(self,request):
        body_unicode = request.body.decode('utf-8')
        # body = json.loads(body_unicode)
        
        print(body_unicode)
        return gen_json_response(status="successs",message="Return your get.",data=body_unicode)

    def post(self,request):
        body_unicode = request.body.decode('utf-8')
        print(body_unicode)
        return gen_json_response(status="successs",message="Return your post.",data=body_unicode)


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
