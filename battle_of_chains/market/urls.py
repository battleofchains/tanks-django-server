from django.urls import path

from .views import MarketPlaceView

app_name = 'market'

urlpatterns = [
    path('marketplace/', MarketPlaceView.as_view(), name='marketplace')
]
