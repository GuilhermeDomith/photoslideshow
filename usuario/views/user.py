from django.shortcuts import render
from django.views import generic
from django.views.generic.edit import CreateView 
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


class UserCreate(CreateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email', 'password']
    #success_url = '/usuario/login'

    def form_valid(self, form):
        # Insere a senha manualmente para que o hash seja gerado.
        user = form.save(commit=False)
        user.set_password(user.password)
        user.save()

        # return HttpResponseRedirect(self.get_success_url())
        return HttpResponseRedirect(reverse('usuario:login'))
