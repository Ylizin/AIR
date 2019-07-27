from django.shortcuts import render,render_to_response

# Create your views here.
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from .models import User

class UserForm(forms.Form): 
    username = forms.CharField(label='用户名',max_length=100)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())

def register(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            #获得表单数据
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            #添加到数据库
            User.objects.create(username= username,password=password)
            return HttpResponse('register success!!')
    else:
        uf = UserForm()
    return render(req,'register.html',{'uf':uf})

def login(req):
    if req.method == 'POST':
        uf = UserForm(req.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']

            use = User.objects.filter(username=username,password=password)
            if use:
                #比较成功，跳转index
                response = HttpResponseRedirect('/online/index/')
                #将username写入浏览器cookie,失效时间为3600
                response.set_cookie('username',username,3600)
                # return render(req,'index.html',{'username':username})
                return response
            else:
                #比较失败，还在login
                return HttpResponseRedirect('/online/login/')
    else:
        uf = UserForm()
    return render(req,'login.html',{'uf':uf})

def index(req):
    username = req.COOKIES.get('username','')
    return render(req,'index.html',{'username':username})

def logout(req):
    response = HttpResponse('logout !!')
    #清理cookie里保存username
    response.delete_cookie('username')
    return response