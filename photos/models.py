from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from google.oauth2.credentials import Credentials
#from oauth2client.contrib.django_orm import CredentialsField


class CredentialsModel(models.Model):
  refresh_token = models.TextField()
  token_uri = models.TextField()
  client_id = models.TextField()
  client_secret = models.TextField()

  def toCredentials(self):
    return Credentials(
              None,  # No access token, must be refreshed.
              refresh_token = self.refresh_token,
              token_uri = self.token_uri,
              client_id = self.client_id,
              client_secret = self.client_secret
            )