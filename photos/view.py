from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from usuario.views import googleauth
from photoslideshow import settings
from photoslideshow.src.slideshow import Slideshow

from datetime import datetime
import threading, json, os, time

URL_LISTAR_ALBUMS = 'https://photoslibrary.googleapis.com/v1/albums'
URL_LISTAR_MIDIAS = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
LONG_PATH_DATA_USERS = settings.BASE_DIR + '/photos/static/photos/data_users'
SHORT_PATH_DATA_USERS = '/static/photos/data_users'

# Armazena o progresso de cada slideshow sendo criado.
STATUS_VIDEOS = {}
# Numero de fotos permitidas em cada slideshow.
MAX_FOTOS = 30


class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'photos/index.html'
    context_object_name = 'albuns'
    ''' Opcional
	login_url = '/login/'
	redirect_field_name = 'redirect_to'
	'''

    def get_queryset(self):
        """
        Obtém os albuns a serem listados na página.
        """

        ''' Retirar apos termino '''
        if 'albuns' not in self.request.session:
            albuns = self.session_photos.get(URL_LISTAR_ALBUMS)
            self.request.session['albuns'] = albuns.json()['albums']

        return self.request.session['albuns']

    def get(self, request, *args, **kwargs):
        """
        Verifica se usuário já autorizou o acesso ao google photos, senão redireciona
        para a página de autorização.
        """
        self.session_photos = googleauth.get_session(request.user)

        if not self.session_photos:
            return HttpResponseRedirect(reverse('usuario:auth_photos'))
        else:
            return super().get(self, request, *args, **kwargs)


@login_required
def selecao(request, num_album):
    if num_album < 1 or num_album > len(request.session['albuns']):
        raise Http404("Album não não encontrado.")

    # Gera um número para identificar o slideshow configurado no momento.
    slideshow_info = {'codigo': int(datetime.now().timestamp())}
    slideshow_info['album'] = request.session['albuns'][num_album - 1]
    slideshow_info['album']['numero'] = num_album

    # Lista as mídias do album através da API do Google Photos.
    info_midias = download_info_midias_album(
        request.user, slideshow_info['album']['id'])

    # Armazena os dados das fotos na sessão.
    slideshow_info['album']['fotos'] = info_midias
    request.session['slideshow'] = slideshow_info

    return render(request, 'photos/selecao.html')


@login_required
def configuracao(request, slideshow_codigo):
    slideshow_info = request.session['slideshow']
    if not slideshow_codigo == slideshow_info['codigo']:
        raise Http404("As fotos selecionadas não foram encontradas.")

    # Verifica se os indices das fotos foram enviados.
    if len(request.POST) != 0:
        # Obtém os índices das fotos selecionadas na view de seleção.
        index_fotos = list(request.POST)[1:]
        fotos_selecionadas = []
        fotos = slideshow_info['album']['fotos']

		# Obtém as fotos que o usuario escolheu, tendo um limite caso seja enviado mais.
        for index in index_fotos[:MAX_FOTOS]:
            fotos_selecionadas.append(fotos[int(index) - 1])

        # Armazena as informações das fotos na sessão.
        slideshow_info['fotos'] = fotos_selecionadas
        request.session['slideshow'] = slideshow_info

    # Se não foi enviado, verifica se existem fotos já selecionadas.
    elif 'fotos' not in slideshow_info:
        raise Http404("As fotos selecionadas não foram encontradas.")

    return render(request,
                  'photos/configuracao.html',
                  {
                      'formatos': Slideshow.VIDEO_TYPE.keys(),
                      'resolucoes': Slideshow.STD_DIMENSIONS.keys()
            })


@login_required
def slideshow(request, slideshow_codigo):

	slideshow_info = request.session['slideshow']
	if not slideshow_codigo == slideshow_info['codigo']:
		raise Http404("As fotos selecionadas não foram encontradas.")

	# Verifica se as configurações de video foram enviados.
	if len(request.POST) != 0:
		# Obtém as configurações do slideshow.
		slideshow_info['conf'] = {}
		slideshow_info['conf']['formato'] = request.POST['formato']
		slideshow_info['conf']['resolucao'] = request.POST['resolucao']
		slideshow_info['conf']['segundos_foto'] = int(
			request.POST['segundos_foto'])

		request.session['slideshow'] = slideshow_info
	# Se não, verifica se existe configuração já fornecida.
	elif 'conf' not in slideshow_info:
		raise Http404("Nenhuma configuração de vídeo foi fornecida.")

	path_album = '{path}/{user}/albuns/{id}'.format(path=LONG_PATH_DATA_USERS,
                                                    user=request.user,
                                                    id=slideshow_info['album']['id'])

	# Cria os diretórios do usuario se não existirem.
	os.makedirs(path_album, exist_ok=True)

	session = googleauth.get_session(request.user)

	for foto_info in slideshow_info['fotos']:
		download_imagem(session, path_album, foto_info)

	path_saida = '{path}/{user}/videos'.format(path=LONG_PATH_DATA_USERS, user=request.user)
	os.makedirs(path_saida, exist_ok=True)
	request.session['slideshow'] = slideshow_info

	threading.Thread(
		target=criar_slideshow,
		args=(request, path_album, path_saida),
		name="Criar Slideshow"
	).start()

	return render(request, 'photos/slideshow.html')



@login_required
def check_progress(request, slideshow_codigo):

	chave = str(request.user) + str(slideshow_codigo)
	if chave not in STATUS_VIDEOS:
		return HttpResponse(0)
	else:
		status_video = STATUS_VIDEOS[chave]

		if status_video['status'] == True:
			del STATUS_VIDEOS[chave]

		return HttpResponse(json.dumps(status_video))



def download_imagem(session_photos, path, foto_info):
	try:
		path_foto = '{path}/{file_name}'.format(path=path, file_name=foto_info['filename'])

		if not os.path.exists(path_foto):
			res = session_photos.get('{url}=d'.format(url=foto_info['baseUrl']))
			
			with open(path_foto, 'wb') as foto:
				foto.write(res.content)
	except:
		raise 'Erro ao fazer dowload da imagem %s \n response: %s' % (
			foto_info['filename'], res.text)



def download_info_midias_album(user=None, id_album=None):
	session = googleauth.get_session(user)

	data = {
		'pageSize': 100,
		'albumId': id_album,
	}

	info_midias = []
	while True:
		response = session.request(
			'POST',
			URL_LISTAR_MIDIAS,
			data
		)

		album_req = json.loads(response.text)
		info_midias += album_req['mediaItems']

		# Verifica se existe mais mídias, pois o limite é 100 por requisição.
		if 'nextPageToken' in album_req:
			data['pageToken'] = album_req['nextPageToken']
		else:
			break

	print('\n\n->Nume de midias:  ', len(info_midias))
	return info_midias



def criar_slideshow(request, path_album, path_saida):
	slideshow_info = request.session['slideshow']

	video = Slideshow(
		path_album,
		path_saida,
		video_filename=slideshow_info['codigo'],
		video_type=slideshow_info['conf']['formato'],
		std_dimension=slideshow_info['conf']['resolucao'],
		segundos_por_img=slideshow_info['conf']['segundos_foto'],
		fotos_filename=[foto['filename'] for foto in slideshow_info['fotos']]
	)

	threading.Thread(
		target=video.criar,
		args=()
	).start()

	chave = str(request.user) + str(slideshow_info['codigo'])

	STATUS_VIDEOS[chave] = {}
	STATUS_VIDEOS[chave]['path'] =  video.absolute_path.replace(LONG_PATH_DATA_USERS, SHORT_PATH_DATA_USERS)

	while not video.terminado:
		STATUS_VIDEOS[chave]['status'] = (video.fotos_inseridas / len(slideshow_info['fotos'])) * 100

	STATUS_VIDEOS[chave]['status'] = video.terminado

