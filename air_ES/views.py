from django.shortcuts import render
from django.http import JsonResponse
from .ES.ES_query import query_text
# Create your views here.


def get_query_result(request,text='美国 cool'):
    return JsonResponse({'texts':query_text(text)})