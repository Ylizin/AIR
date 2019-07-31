from django.shortcuts import render,reverse
from django.http import JsonResponse,HttpResponseRedirect
from django.views import View
from .query_result import *
from .query_result import get_rough_query_result as get_query_result
# from django.contrib.auth import login_required
# Create your views here.




# TODO: the first page invokation calculation
# TODO: encapsulation of the session access
class RecView(View):
    def get(self,request,*args,**kwargs):
        # if not request.session.get('is_logined',False):
            # return HttpResponseRedirect('/login') 

        #get user id in GET
        _usr_id = request.GET.get('_id',None)
        user_tag0,user_tag1,use_info = get_user_tags(_usr_id)
        _dummy_user_text = [('word embedding',1.0),('graph embedding',2.0)]
        rough_info = get_rough_query_result(_dummy_user_text)
        recommends = get_acc_query_result(use_info,rough_info)
        return JsonResponse({'texts':recommends})


class RecView_News(View):
    def get(self,request,*args,**kwargs):
        # if not request.session.get('is_logined',False):
            # return HttpResponseRedirect('/login') 

        #get user id in GET
        _usr_id = request.GET.get('_id',None)
        user_tag0,user_tag1,use_info = get_user_tags(_usr_id)
        _dummy_user_text = [('机器学习',1.0),('nlp',2.0)]
        rough_info = get_rough_query_result(_dummy_user_text,index='news',fields=[('content',4),('title',10)])
        print("############")
        
        recommends = get_acc_query_result(use_info,rough_info)
        print(recommends)
        return JsonResponse({'type':'news','texts':recommends})