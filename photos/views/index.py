from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from usuario.views import googleauth
from photoslideshow import settings

import threading, json, os

URL_LISTAR_ALBUMS = 'https://photoslibrary.googleapis.com/v1/albums'
URL_LISTAR_MIDIAS = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
PATH_IMAGENS = settings.BASE_DIR + '/photos/static/photos/img/'

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


def slideshow(request, num_album):
	album = request.session['albuns'][num_album - 1]
	album_key = 'album_'+album['id']
	path = PATH_IMAGENS+album_key

	if album_key not in request.session:
		session = googleauth.get_session(request.user)
		data_search = dict(
			pageSize=100,
			albumId=album['id']
		)
		response = session.request('POST', URL_LISTAR_MIDIAS, data=data_search)
		request.session[album_key] = json.loads(response.text)['mediaItems']

		if not os.path.exists(path):
			os.mkdir(path)
	
		for foto in request.session[album_key]:
			download_imagem(session, path, foto)

	return render(request, 'photos/slideshow.html', {
		'album_key': album_key,
		'fotos': request.session[album_key]
		})


def download_imagem(session, path, foto_info):
	response = session.get(foto_info['baseUrl'] + '=d')

	try:
		with open(path+'/'+foto_info['filename'], 'wb') as foto:
			foto.write(response.content)
	except Exception as e:
		print(e+'\n'+foto_info)
