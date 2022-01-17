from django.http import HttpResponse
from django.views import View

from .models import GamePage, IndexPage


class IndexView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return HttpResponse(IndexPage.get_solo().html)


class GameView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return HttpResponse(GamePage.get_solo().html)
