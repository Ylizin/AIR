from django.shortcuts import render,reverse
from django.http import JsonResponse,HttpResponseRedirect
from django.views import View
from .query_result import *
import json
from .query_result import get_rough_query_result as get_query_result
# from django.contrib.auth import login_required
# Create your views here.




# TODO: encapsulation of the session access
class RecView(View):
    def get(self,request,*args,**kwargs):
        # if not request.session.get('is_logined',False):
            # return HttpResponseRedirect('/login') 

        #get user id in GET
        texts = {}
        _usr_id = request.GET.get('uid',None)
        text_w,use_info = get_user_tags(_usr_id)
        '''--------------for debug---------------------'''
        # text_w = [('word embedding',1.0),('graph embedding',2.0)]

        arxiv_info = get_rough_query_result(text_w,index='arxiv')
        news_info = get_rough_query_result(text_w,index = 'news')
        github_info = get_rough_query_result(text_w,index = 'github')

        arxiv_info = get_acc_query_result(use_info,arxiv_info,index='arxiv')
        news_info = get_acc_query_result(use_info,news_info,index = 'news')
        github_info = get_acc_query_result(use_info,github_info,index = 'github')
        
        recommends = arxiv_info+news_info+github_info
        texts['texts'] = recommends
        
        return JsonResponse(texts)

class SearchView(View):
    def get(self,request,*args,**kwargs):
        # if not request.session.get('is_logined',False):
            # return HttpResponseRedirect('/login') 
        texts = {}
        #get keyword and give it a weight 
        # post = json.loads(request.body)
        
        keywords = request.GET.get('keywords',None)
        if not keywords:
            return JsonResponse({'message':'Nothing to search.','flag':0})
        text_w = [(keywords,1)]
        # text_w = [(word,1) for word in keywords]
        arxiv_info = get_rough_query_result(text_w,index='arxiv')
        news_info = get_rough_query_result(text_w,index = 'news')
        github_info = get_rough_query_result(text_w,index = 'github')
        recommends = arxiv_info+news_info+github_info
        texts['texts'] = recommends
        return JsonResponse(texts)

class RecView_News(View):
    def get(self,request,*args,**kwargs):
        # if not request.session.get('is_logined',False):
            # return HttpResponseRedirect('/login') 

        #get user id in GET
        _usr_id = request.GET.get('_id',None)
        text_w,use_info = get_user_tags(_usr_id)
        _dummy_user_text = [('机器学习',1.0),('nlp',2.0)]
        rough_info = get_rough_query_result(_dummy_user_text,index='news',fields=[('content',4),('title',10)])
        print("############")
        
        recommends = get_acc_query_result(use_info,rough_info,index='news')
        return JsonResponse({'type':'news','texts':recommends})