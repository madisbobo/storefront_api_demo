from django.shortcuts import render
from django.http import HttpResponse

# Create your views here. It like a controller in Java, request handler (takes request and returns a response)

def calculate():
    x = 1
    y = 2
    return x

def say_hello(reuqest):
    x = calculate()
    return render(reuqest, 'hello.html', {'name': 'Madis'})

def help(request):
    return HttpResponse("This is help page")



