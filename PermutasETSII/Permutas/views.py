from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader


# Create your views here.

def permutas(request):
    template = loader.get_template('home.html')
    return HttpResponse(template.render())

def nuevaPermutas(request):
    template = loader.get_template('nueva-permuta.html')
    return HttpResponse(template.render())

def todasPermutas(request):
    template = loader.get_template('permutas.html')
    return HttpResponse(template.render())