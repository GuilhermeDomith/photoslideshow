import json
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect

from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import Flow

from photos.models import CredentialsModel
from animaphotos import settings



scopes=['https://www.googleapis.com/auth/photoslibrary.readonly']

FLOW = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENTE_CREDENTIALS_JSON,
            scopes=scopes, 
            redirect_uri='http://localhost:8000/photos/return_auth'
            )

session = None

def return_auth(request):
    '''
    Grava a credencial do usuário que permitiu o acesso ao google photos. 
    Esta view deve ser chamada no retorno da autorização, ou seja, no redirect_uri 
    do flow criado. Se a autorização foi bem sucedida o parametro CODE da URL será usado 
    para gerar a credencial.
    '''
    global session

    code = request.GET['code']
    FLOW.fetch_token(code=code)
    credentials = FLOW.credentials

    model = CredentialsModel()
    model.refresh_token = credentials.refresh_token
    model.token_uri = credentials.token_uri
    model.client_id = "554833195435-viajnbdvm9ro2tgodotgr6fpqpa9notu.apps.googleusercontent.com"
    model.client_secret = "chfSrjyrbXwob2A3nG3JZxcP"
    model.save()

    session = AuthorizedSession(credentials)
    return HttpResponseRedirect(reverse('photos:index'))


def auth_photos(request):
    '''
      Verifica se existe credencial salva para o usuário logado. Caso exista redireciona para 
      a página inicial da aplicação, se não, redireciona para a página do google em que o 
      usuário deve autorizar o acesso ao google photos.
    '''
    global session

    credentials = None 
    lista = CredentialsModel.objects.all()

    if len(lista) > 0:
      credentials = lista[0].toCredentials()

    if not credentials:
      auth_url, _ = FLOW.authorization_url(prompt='consent')
      return HttpResponseRedirect(auth_url)
    
    session = AuthorizedSession(credentials)
    return HttpResponseRedirect(reverse('photos:index'))

def get_session():
    return session

