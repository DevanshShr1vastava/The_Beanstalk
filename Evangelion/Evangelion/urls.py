"""
URL configuration for Evangelion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from eva01.views import home,arena,hyoka,test_complete_page, analyse
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name='homePage'),
    path('arena/',arena,name='fightHere'),
    path('hyoka/<int:qpID>/<int:qID>',hyoka,name="hyoka"),
    path('test_complete_page/',test_complete_page,name='test_complete_page'),
    path('analysis/',analyse,name='analyse')
    
]
