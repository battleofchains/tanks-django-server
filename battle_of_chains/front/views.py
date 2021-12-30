from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
from battle_of_chains.battle.models import Tank
from .models import GamePage, IndexPage


class IndexView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return HttpResponse(IndexPage.get_solo().html)


class GameView(View):
    # noinspection PyMethodMayBeStatic
    def get(self, request):
        return HttpResponse(GamePage.get_solo().html)


class MarketPlaceView(ListView):
    queryset = Tank.objects.filter(for_sale=True)
    template_name = 'pages/marketplace.html'
