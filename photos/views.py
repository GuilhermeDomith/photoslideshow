from django.shortcuts import render
from django.views import generic

class IndexView(generic.ListView):
    template_name = 'photos/index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return 'Festa 2 anos, Aniversario 3, Casamento'.split(',')