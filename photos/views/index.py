from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from usuario.views import googleauth
from photoslideshow import settings

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


def slideshow(request, num_album):
	if num_album < 1 or num_album > len(request.session['albuns']):
		return Http404("Este album não existe.")

	album = request.session['albuns'][num_album - 1]
	path_album = '{path}/{user}/albuns/{id}'.format(path=PATH_IMAGENS, user=request.user, id=album['id'])
	print('--->'+path_album)
	if path_album not in request.session:
		session = googleauth.get_session(request.user)
		response = session.request(
						'POST', 
						URL_LISTAR_MIDIAS, 
						data={'pageSize': 100, 'albumId': album['id']}
					)

		request.session[path_album] = json.loads(response.text)['mediaItems']

		if not os.path.exists(path_album):
			os.mkdir(path_album)
	
		for foto_info in request.session[path_album]:
			download_imagem(session, path_album, foto_info)

	return render(request, 'photos/slideshow.html', {
				'album_id': album['id'],
				'fotos': request.session[path_album]
		   })


def download_imagem(session_photos, path, foto_info):
	response = session_photos.get('{url}=d'.format(url=foto_info['baseUrl']))

	try:
		path_foto = '{path}/{file_name}'.format(path=path, file_name=foto_info['filename'])

		if not os.path.exists(path_foto):
			with open(path_foto, 'wb') as foto:
				foto.write(response.content)
	except Exception as e:
		print(e+'\n'+foto_info)
