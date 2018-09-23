from django.shortcuts import render
from django.views import generic
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect

#from .models import CredentialsModel
from animaphotos import settings

from google.auth.transport.requests import AuthorizedSession
from google_auth_oauthlib.flow import InstalledAppFlow

FLOW = InstalledAppFlow.from_client_secrets_file(
            settings.GOOGLE_CLIENTE_CREDENTIALS_JSON,
            scopes=['https://www.googleapis.com/auth/photoslibrary.readonly'],
            redirect_uri='/index')


class IndexView(generic.ListView):
    template_name = 'photos/index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return 'Festa 2 anos, Aniversario 3, Casamento'.split(',')


def login(request):

    credentials = FLOW.run_local_server()
    session = AuthorizedSession(credentials)

    return HttpResponseRedirect(reverse('photos:index'))

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