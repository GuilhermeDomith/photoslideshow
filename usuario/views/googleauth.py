import json
from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect

from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import Flow

from usuario.models import CredentialsModel
from django.contrib.auth.models import User
from photoslideshow import settings
from django.contrib.auth.decorators import login_required

_sessions = {}

_flow = Flow.from_client_secrets_file(
    settings.GOOGLE_CLIENTE_CREDENTIALS_JSON,
    scopes=['https://www.googleapis.com/auth/photoslibrary.readonly'],
    redirect_uri='http://localhost:8000/usuario/return_auth',

)

@login_required
def return_auth(request):
    '''
      Grava a credencial do usuário que permitiu o acesso ao google photos. 
      Esta view deve ser chamada no retorno da autorização, ou seja, no redirect_uri 
      do flow criado. Se a autorização foi bem sucedida o parâmetro CODE da URL será usado 
      para gerar a credencial.
    '''
    global session

    if 'error' in request.GET or 'code' not in request.GET:
        return HttpResponseRedirect(reverse('usuario:permissao'))

    _flow.fetch_token(code=request.GET['code'])
    credentials = _flow.credentials

    print('retorno')
    print(request.GET['code'])
    print(_flow)
    print(credentials)

    model = CredentialsModel()
    model.refresh_token = credentials.refresh_token
    model.token_uri = credentials.token_uri
    model.user = User.objects.get(username=request.user)
    model.save()

    _sessions[request.user] = AuthorizedSession(credentials)
    return HttpResponseRedirect(reverse('photos:index'))

@login_required
def permissao(request):
    '''
      Verifica se existe credencial salva para o usuário logado. Caso exista 
      redireciona para a página inicial da aplicação, se não, redireciona para a 
      página que informa a necessidade da permissão.
    '''
    if get_session(request.user) == None:
        return render(request, 'auth/permissao.html')
    
    return HttpResponseRedirect(reverse('photos:index'))


@login_required
def auth_photos(request):
    '''
    Redireciona para a página do google em que o usuário deve autorizar o acesso 
    ao google photos. Se já existe credencial para o usuário logado redireciona para a 
    página inicial.
    '''
    if get_session(request.user) == None:
        auth_url, _ = _flow.authorization_url(prompt='consent')
        return HttpResponseRedirect(auth_url)

    return HttpResponseRedirect(reverse('photos:index'))


def get_session(username):
	if username in _sessions:
		return _sessions[username]

	try:
		credentials = CredentialsModel.objects.get(user__username=username)
		credentials = credentials.toCredentials( 
			_flow.client_config['client_id'], 
			_flow.client_config['client_secret'])

		_sessions[username] = AuthorizedSession(credentials)
		return _sessions[username]
	except CredentialsModel.DoesNotExist:
		return None
