from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
#from rest_framework.decorators import api_view


from .models import UserProfile

import json

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
        # username = request.POST.get("username")
        # password = request.POST.get("password")
        username = body['username']
        password = body['password']

        interests = "Nothing"
        # interests = body['interests']
      

        #judge if the username is duplicated
        is_duplicated = User.objects.filter(username=username)
        if is_duplicated:
            return gen_json_response(status='error',message='Duplicate username!')
        # initial a user object
        user = User.objects.create_user(
            username=username,
            # email=form.cleaned_data['email'], #todo: add email verification
            password=password,
        )
        # initial user profile
        degree='No degree'
        user_profile = UserProfile(user=user,interests=interests,degree=degree)
        # write to db
        user_profile.save()
        # get user id
        uid = User.objects.get(username=username).pk
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
        interests = body['interests']
        if interests is None:
            interests = "[[{'CV':1.2},{'object detection':0.8},{'SLAM':0.4}],[{'NLP':1.3},{'word embedding':0.7},{'SVD':0.8}]]"
        degree = body['degree']
        print(degree)

        user = UserProfile.objects.filter(user_id=uid).update(interests=interests,degree=degree)
        # if is_duplicated:
        #     return render(request,'account/register.html',{'form': form,'msg':'This name has existed.'})
        # initial a user object
 
        # initial user profile
        print("@@@@@@@@@@@@@")
        print(interests)
        # user.interests = interests
        # user.degree = degree
        # # write to db
        # user.save()
        # uid = User.objects.get(username=username).pk
        print('save success.')
        return gen_json_response(status="success",message="Register interests success!")

        # return JsonResponse(data={'message':'hi react from remote server.kiddding?'})
        # return render(request, self.template_name, {'form': form})


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
            
            # todo: if speed is too slow, we can redesign the models.py for database
            # reformat input for query 
            interests = json.loads(user.interests)
            mytuple = next(iter(interests[0][0].items()))
            query_text_raw = user.interests
            query_text = [ next(iter(x.items())) for item in query_text_raw for x in item ]
            
            # expected input: [("CV",1.0),("nlp",10.0)]
            paper_list = get_rough_query_result(query_text)
            data = {"uid":uid,"paper_list":paper_list}
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