from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from .models import UserForm

import json

# def __get_response_json_dict(data, err_code=0, message="success"):
#     ret = {
#     'err_code': err_code,
#     'message': message,
#     'data': data
#     }
#     return ret


class RegisterView(View):
    form_class = UserForm  # models.py中自定义的表单
    template_name = 'account/register.html'

    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self,request):
        # received_data = json.loads(request.body.decode('utf-8'))
        # username = received_data["username"]
        # password = received_data["password"]

        form = self.form_class(request.POST)
        
        if form.is_valid():
            for item in form.cleaned_data:
                print(form.cleaned_data[item])
            print("!!!!!!!!!!!!")
            username = form.cleaned_data['username']
            user = self.model(username=username, email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                # email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                initial_tag_0=form.cleaned_data['initial_tag_0'],
                # initial_tag_1=form.cleaned_data['initial_tag_1'],
            )
            # 保存到数据库中
            user.save()
            # TODO: 查重 
            return render(request, 'account/register_success.html', {'form': form})
        return render(request, self.template_name, {'form': form})

        # return JsonResponse(__get_response_json_dict(data={}))

class LoginView(View):
    form_class = UserForm  # models.py中自定义的表单
    template_name = 'account/login.html'
    
    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self,request):
        # received_data = json.loads(request.body.decode('utf-8'))
        # username = received_data["username"]
        # password = received_data["password"]
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']

            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                # return JsonResponse(__get_response_json_dict(data={}))
                # response.set_cookie('username',username,3600)
                return render(request, 'index.html', {'username':username})
            else:
                # return JsonResponse(__get_response_json_dict(data={}, err_code=-1, message="Invalid username or password"))
                return render(request, self.template_name, {'username':username})


class LogoutView(View):
    form_class = UserForm  # models.py中自定义的表单

    def post(self,request):
        form = self.form_class(None)
        logout(request)
        return render(request,'account/login.html', {'form': form})
        # return JsonResponse(__get_response_json_dict(data={}))
