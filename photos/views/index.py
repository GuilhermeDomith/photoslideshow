from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from usuario.views import googleauth


class IndexView(LoginRequiredMixin, generic.ListView):
	template_name = 'photos/index.html'
	context_object_name = 'albuns'
	''' Opcional
	login_url = '/login/'
	redirect_field_name = 'redirect_to'
	'''

	def get_queryset(self):
		session = googleauth.get_session(self.request.user)

		if not session:
			return ""
		else:
			albuns = session.get('https://photoslibrary.googleapis.com/v1/albums')
			self.request.session['albuns'] = albuns.json()['albums']
			return self.request.session['albuns']

	
