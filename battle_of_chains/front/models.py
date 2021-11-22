from django.db import models
from solo.models import SingletonModel


class IndexPage(SingletonModel):
    html = models.TextField('html')
    updated = models.DateTimeField('updated', auto_now=True)


class GamePage(SingletonModel):
    html = models.TextField('html')
    updated = models.DateTimeField('updated', auto_now=True)
