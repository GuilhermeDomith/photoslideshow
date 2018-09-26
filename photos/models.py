from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

#from oauth2client.contrib.django_orm import CredentialsField


class CredentialsModel(models.Model):
  #id = models.ForeignKey(User, primary_key=True)
  refresh_token = models.TextField()
  token_uri = models.TextField()
  client_id = models.TextField()
  client_secret = models.TextField()

'''
class CredentialsAdmin(admin.ModelAdmin):
    pass
'''


'''
from oauth2client.contrib.django_orm import CredentialsField
from google.


class CredentialsModel(models.Model):
  id = models.ForeignKey(User, primary_key=True)
  credential = CredentialsField()


class CredentialsAdmin(admin.ModelAdmin):
    pass
'''