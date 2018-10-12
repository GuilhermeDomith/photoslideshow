from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from usuario.views import googleauth
from photoslideshow import settings
from photoslideshow.src.slideshow import Slideshow

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
		albuns = self.session_photos.get(URL_LISTAR_ALBUMS)
		self.request.session['albuns'] = albuns.json()['albums']
		return self.request.session['albuns']


	def get(self, request, *args, **kwargs):
		self.session_photos = googleauth.get_session(request.user)

		if not self.session_photos:
			return HttpResponseRedirect(reverse('usuario:auth_photos'))
		else:
			return super().get(self, request, *args, **kwargs)

@login_required
def selecao(request, num_album):
	if num_album < 1 or num_album > len(request.session['albuns']):
		raise Http404("Album não não encontrado.")

	album = request.session['albuns'][num_album - 1]
	session = googleauth.get_session(request.user)
	response = session.request(
					'POST', 
					URL_LISTAR_MIDIAS, 
					data={'pageSize': 100, 'albumId': album['id']}
				)

	album_id = album['id']
	request.session[album_id] = json.loads(response.text)['mediaItems']
	return render(request, 
				'photos/selecao.html', 
				{ 'album_id': album_id, 'fotos_info': request.session[album_id]})

	
@login_required
def slideshow(request, album_id):
	if album_id not in request.session:
		raise Http404("As fotos selecionadas não foram encontradas.")

	fotos_info = request.session[album_id]
	index_fotos = list(request.POST)[1:]
	path_album = '{path}/{user}/albuns/{id}'.format(path=PATH_IMAGENS, user=request.user, id=album_id)
	
	if not os.path.exists(path_album):
		os.mkdir(path_album)

	session = googleauth.get_session(request.user)
	for index in index_fotos:
		download_imagem(session, path_album, fotos_info[int(index)-1])

	path_saida = '{path}/{user}/videos'.format(path=PATH_IMAGENS, user=request.user)
	video_slideshow = Slideshow(path_album, path_saida, video_filename='teste')
	video_slideshow.criar()

	return render(request, 'photos/slideshow.html', {
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
