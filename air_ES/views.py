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
        user_tag0,user_tag1 = get_user_tags(_usr_id)
        _dummy_user_text = 'data'
        return JsonResponse(get_query_result(request,_dummy_user_text))


