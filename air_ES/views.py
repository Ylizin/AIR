from django.shortcuts import render,reverse
from django.http import JsonResponse,HttpResponseRedirect
from django.views import View
from .query_result import get_rough_query_result as get_query_result
# from django.contrib.auth import login_required
# Create your views here.





class RecView(View):
    def get(self,request,*args,**kwargs):
        # if not request.session.get('is_logined',False):
            # return HttpResponseRedirect('/login') 

        #get user id in GET
        _usr_id = request.GET.get('_id',None)
        _dummy_user_text = 'data'
        return get_query_result(request,_dummy_user_text)


