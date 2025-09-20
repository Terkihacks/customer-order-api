from django.shortcuts import render
from django.http import HttpResponse
from django.views import View 
# Create your views here.

def hell(request):
    return HttpResponse("Hello, World!")

class HelloKenya:
    def get(self, request):
        return HttpResponse("Hello, Kenya!")
    