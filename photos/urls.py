from django.urls import path
from . import  views

app_name = 'photos'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),  
    path('', views.login, name='login'), 
    #path('<>', views.login, name='logar'),   
]