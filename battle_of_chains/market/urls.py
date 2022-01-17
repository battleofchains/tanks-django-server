from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import MarketPlaceView

app_name = 'market'

urlpatterns = [
    path('marketplace/', login_required(MarketPlaceView.as_view()), name='marketplace')
]
