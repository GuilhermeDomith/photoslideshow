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
import threading, json, os

URL_LISTAR_ALBUMS = 'https://photoslibrary.googleapis.com/v1/albums'
URL_LISTAR_MIDIAS = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
PATH_IMAGENS = settings.BASE_DIR + '/photos/static/photos/data_users'

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

	# Obtém o número que será usado para identificar o slideshow
	slideshow_info = {'codigo': int(datetime.now().timestamp())}
	slideshow_info['album'] = request.session['albuns'][num_album - 1]

	session = googleauth.get_session(request.user)
	response = session.request(
					'POST', 
					URL_LISTAR_MIDIAS, 
					data={
						'pageSize': 100, 
						'albumId': slideshow_info['album']['id']
					}
				)

	slideshow_info['album']['fotos'] = json.loads(response.text)['mediaItems']
	request.session['slideshow'] = slideshow_info

	return render(request, 'photos/selecao.html')

@login_required
def configuracao(request, slideshow_codigo):
	slideshow_info = request.session['slideshow']
	if not slideshow_codigo == slideshow_info['codigo']:
		raise Http404("As fotos selecionadas não foram encontradas.")

	index_fotos = list(request.POST)[1:]
	fotos_selecionadas = []
	fotos = slideshow_info['album']['fotos']

	for index in index_fotos:
		fotos_selecionadas.append(fotos[int(index) - 1])

	slideshow_info['fotos'] = fotos_selecionadas
	request.session['slideshow'] = slideshow_info
	print('1 --> '+ str(request.session['slideshow']) + '\n\n')

	return render(request, 
				'photos/configuracao.html',
				{	
					'formatos': Slideshow.VIDEO_TYPE.keys(), 
					'resolucoes': Slideshow.STD_DIMENSIONS.keys()
				}
			)
	
@login_required
def slideshow(request, slideshow_codigo):
	
	slideshow_info = request.session['slideshow']
	if not slideshow_codigo == slideshow_info['codigo']:
		raise Http404("As fotos selecionadas não foram encontradas.")

	slideshow_info['formato'] = request.POST['formato']
	slideshow_info['resolucao'] = request.POST['resolucao']
	print('2 --> '+ str(request.session['slideshow']) + '\n\n')

	path_album = '{path}/{user}/albuns/{id}'.format(path=PATH_IMAGENS, 
													user=request.user, 
													id=slideshow_info['album']['id'])
	
	#if not os.path.exists(path_album):
	os.makedirs(path_album, exist_ok=True)

	session = googleauth.get_session(request.user)
	for foto_info in slideshow_info['fotos']:
		download_imagem(session, path_album, foto_info)

	path_saida = '{path}/{user}/videos'.format(path=PATH_IMAGENS, user=request.user)
	os.makedirs(path_saida, exist_ok=True)

	video_slideshow = Slideshow(
							path_album, 
							path_saida, 
							video_filename = slideshow_info['codigo'], 
							video_type = slideshow_info['formato'], 
							std_dimension = slideshow_info['resolucao'],
							fotos_filename = [foto['filename'] for foto in slideshow_info['fotos']]
					)
	video_slideshow.criar()

	return render(request, 'photos/slideshow.html', {
				# Obtém apenas o caminho após  static/photos/data_users/
				'path_video': video_slideshow.absolute_path.replace(PATH_IMAGENS, '')
		   })


def download_imagem(session_photos, path, foto_info):
	response = session_photos.get('{url}=d'.format(url=foto_info['baseUrl']))

	try:
		path_foto = '{path}/{file_name}'.format(path=path, file_name=foto_info['filename'])
		if not os.path.exists(path_foto):
			with open(path_foto, 'wb') as foto:
				foto.write(response.content)
	except:
		raise 'Erro ao fazer dowload da imagem %s'%foto_info['filename']
