import platform

from django.db import models


class Bacula(models.Model):
    """
    Django model describing every tunable setting for transmission
    """

    enable = models.BooleanField(default=False)
    allowed = models.TextField(blank=True)
    blocklist = models.TextField(blank=True)
