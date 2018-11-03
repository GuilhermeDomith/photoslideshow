from django.urls import path
from usuario.views import googleauth, user
from django.contrib.auth import views as auth_views

app_name = 'usuario'

urlpatterns = [
    # Automaticamente irá buscar o template na pasta registration. 
    # settings.LOGIN_REDIRECT_URL
    path('login/', auth_views.LoginView.as_view(), name='login'), 
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cadastro/', user.UserCreate.as_view(), name='cadastro'),

    path('permissao/', googleauth.permissao, name='permissao'),
    path('auth_photos/', googleauth.auth_photos, name='auth_photos'),
    path('return_auth/', googleauth.return_auth, name='return_auth')
]