from django.shortcuts import render
from django.views import generic
from django.urls import reverse

#from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect

from .models import CredentialsModel
from animaphotos import settings

from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
#from google.oauth2 import service_account
#from oauth2client import client, tools


scopes=['https://www.googleapis.com/auth/photoslibrary.readonly']

FLOW = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENTE_CREDENTIALS_JSON,
            scopes=scopes, 
            redirect_uri='http://localhost:8000/photos/return_auth'
            )


class IndexView(generic.ListView):
    template_name = 'photos/index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return 'Festa 2 anos, Aniversario 3, Casamento'.split(',')


def return_auth(request):
  '''
    Grava a credencial do usuário que permitiu o acesso ao google photos. 
    Esta view deve ser chamada no retorno da autorização, ou seja, no redirect_uri 
    do flow criado. Se a autorização foi bem sucedida o parametro CODE da URL será usado 
    para gerar a credencial.
  '''
  code = request.GET['code']
  FLOW.fetch_token(code=code)
  credentials = FLOW.credentials

  model = CredentialsModel()
  model.refresh_token = credentials.refresh_token
  model.token_uri = credentials.token_uri
  model.client_id = "554833195435-viajnbdvm9ro2tgodotgr6fpqpa9notu.apps.googleusercontent.com"
  model.client_secret = "chfSrjyrbXwob2A3nG3JZxcP"
  model.save()

  return HttpResponseRedirect(reverse('photos:index'))


def auth_photos(request):
    '''
      Verifica se existe credencial salva para o usuário logado. Caso exista redireciona para 
      a página inicial da aplicação, se não, redireciona para a página do google em que o 
      usuário deve autorizar o acesso ao google photos.
    '''
    credentials = None 
    lista = CredentialsModel.objects.all()

    if len(lista) > 0:
      credentials = lista[0]

    if not credentials:
      auth_url, _ = FLOW.authorization_url(prompt='consent')
      return HttpResponseRedirect(auth_url)
    
    '''
    credentials = montarCredentials(credentials)
    session = AuthorizedSession(credentials)
    '''
    return HttpResponseRedirect(reverse('photos:index'))


def montarCredentials(credentials_model):
  credentials_model = CredentialsModel()
  credentials = Credentials(
        None,  # No access token, must be refreshed.
        refresh_token = credentials_model.refresh_token,
        token_uri = credentials_model.token_uri,
        client_id = credentials_model.client_id,
        client_secret = credentials_model.client_secret)

  return credentials

'''
@login_required
def index(request):
  storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
  credential = storage.get()
  if credential is None or credential.invalid == True:
    
    FLOW.params['state'] = xsrfutil.generate_token(settings.SECRET_KEY,
                                                   request.user)
    authorize_url = FLOW.step1_get_authorize_url()
    return HttpResponseRedirect(authorize_url)
    
    print('\n\nCredencial ninvalida!\n\n')
  else:
    credentials = FLOW.run_local_server()
    session = AuthorizedSession(credentials)
    #response = session.get(URL_LISTAR_ALBUMS)

    return render(request, 'photos/index.html', {
                'albums': ['teste1', 'teste2'],
                })

@login_required
def auth_return(request):
  if not xsrfutil.validate_token(settings.SECRET_KEY, request.REQUEST['state'],
                                 request.user):
    return  HttpResponseBadRequest()
  credential = FLOW.step2_exchange(request.REQUEST)
  storage = DjangoORMStorage(CredentialsModel, 'id', request.user, 'credential')
  storage.put(credential)
  return HttpResponseRedirect("/")
  '''