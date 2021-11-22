from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import GameView, IndexView

app_name = 'front'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('game/', login_required(GameView.as_view()), name='game'),
]
