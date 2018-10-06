from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from google.oauth2.credentials import Credentials


class CredentialsModel(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  refresh_token = models.TextField()
  token_uri = models.TextField()

  def toCredentials(self, client_id, client_secret):
    return Credentials(
              None,  # No access token, must be refreshed.
              refresh_token = self.refresh_token,
              token_uri = self.token_uri,
              client_id = client_id,
              client_secret = client_secret
            )
