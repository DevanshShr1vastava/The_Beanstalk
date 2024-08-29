from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"home.html")
def dashboard(request):
    return render(request,"dashboard.html")
def mcq(request):
    return render(request,"mcq.html")
def about_us(request):
    return render(request,"about_us.html")