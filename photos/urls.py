from django.urls import path
from photos.views import  auth, init

app_name = 'photos'

urlpatterns = [
    path('index/', init.IndexView.as_view(), name='index'), 

    path('', auth.auth_photos, name='auth_photos'),
    path('return_auth/', auth.return_auth, name='return_auth')
    #path('<>', auth.login, name='logar'),   
]