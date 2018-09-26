from django.shortcuts import render
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect

from photos.views import auth

class IndexView(generic.ListView):
    template_name = 'photos/index.html'
    context_object_name = 'albuns'
    albuns = None

    def get_queryset(self):
      session = auth.get_session()
      return session.get('https://photoslibrary.googleapis.com/v1/albums').json()['albums']
