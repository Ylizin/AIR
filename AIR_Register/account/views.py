from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator


from .models import UserProfile
from .forms import RegisterForm,LoginForm

import json

def get_response_json_dict(data, err_code=0, message="success"):
    ret = {
    'err_code': err_code,
    'message': message,
    'data': data
    }
    return ret


class RegisterView(View):
    template_name = 'account/register.html'

    def get(self,request):
        form = RegisterForm(request.POST)
        return render(request, self.template_name, {'form': form}) #TODO:form清空？

    def post(self,request):
        # received_data = json.loads(request.body.decode('utf-8'))
        # username = received_data["username"]
        # password = received_data["password"]
        # interests = received_data["password"]
        username = 'keyerror'
        print(request.POST)
        # username = request.POST['username']
        # password = request.POST['password']
        print(username)
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        # username = received_data["username"]
        # password = received_data["password"]
        # interests = received_data["password"]
        print(request.POST)
        # username = request.POST.get("username")
        # password = request.POST.get("password")
        username = body['username']
        password = body['password']
        interests = "[{'CV':['object detection']},{'NLP':['object detection']"
        # form = RegisterForm(request.POST)
        interests = body['interests']
        # if form.is_valid():
            # username = form.cleaned_data['username']
            # password = form.cleaned_data['password']
            # interests = form.cleaned_data['interests']
            # initial_tag_1 = form.cleaned_data['initial_tag_1']
            
            #judge if the username is replicated
        is_duplicated = User.objects.filter(username=username)
        # if is_duplicated:
        #     return render(request,'account/register.html',{'form': form,'msg':'This name has existed.'})
        # initial a user object
        user = User.objects.create_user(
            username=username,
            # email=form.cleaned_data['email'],
            password=password,
        )
        # initial user profile
        user_profile = UserProfile(user=user,interests=interests)
        # write to db
        user_profile.save()
        uid = User.objects.get(username=username).pk
        print('save success.')
        data = {'status':'success','message':'Register success!','data':{'uid':uid}}
        return JsonResponse(data)

        # return JsonResponse(data={'message':'hi react from remote server.kiddding?'})
        # return render(request, 'account/register_success.html', {'form':form})

        # return render(request, self.template_name, {'form': form})

        # return JsonResponse(__get_response_json_dict(data={}))

class LoginView(View):
    template_name = 'account/login.html'
    
    def get(self,request):
        # form = LoginForm(None)
        #return render(request, self.template_name, {'form': form})
        return JsonResponse(data={'message':'hi react from remote server.kiddding?'})

    def post(self,request):
        # received_data = json.loads(request.body.decode('utf-8'))
        # username = received_data["username"]
        # password = received_data["password"]
        user_form = LoginForm(request.POST)

        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # return JsonResponse(__get_response_json_dict(data={}))
                # response.set_cookie('username',username,3600)
                return render(request, 'account/index.html', {'username':username})
            else:
                # return JsonResponse(__get_response_json_dict(data={}, err_code=-1, message="Invalid username or password"))
                return render(request, self.template_name, {'form': user_form,'message': 'Wrong password or account. Please try again.'})

        # return HttpResponseRedirect("/account/login")

class LogoutView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        logout(request)
        print('log out ..............')
        username = request.POST.get('username')
        print("dsd"+str(username))
        # return render(request,'account/login.html', {'message': 'Logout success.'})
        return HttpResponseRedirect('/account/login')
    def post(self,request):
        # form = LoginForm(None)
        logout(request)
        print('log out ..............')
        username = request.POST.get('username')
        print("dsd"+str(username))
        # return render(request,'account/login.html', {'form': form,'message': 'Logout success.'})
        return HttpResponseRedirect('/account/login')
        # return JsonResponse(__get_response_json_dict(data={}))

@method_decorator(login_required, name='dispatch')
class IndexView(View):
    # form_class = UserForm  # models.py中自定义的表单
    def get(self,request):
        # form = LoginForm(None)
        # return render(request,'account/login.html', {'form': form,'message': 'Logout success.'})
        return render(request, 'account/index.html')
        # return HttpResponseRedirect("account/index.html")
        # return JsonResponse(__get_response_json_dict(data={}))
