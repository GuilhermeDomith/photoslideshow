from django.urls import path
from . import  views

app_name = 'photos'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'), 
    path('', views.auth_photos, name='auth_photos'),
    path('return_auth/', views.return_auth, name='return_auth')
    #path('<>', views.login, name='logar'),   
]