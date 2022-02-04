from django.urls import path

from .views import MarketPlaceDetailView, MarketPlaceView

app_name = 'market'

urlpatterns = [
    path('', MarketPlaceView.as_view(), name='marketplace'),
    path('<int:pk>/', MarketPlaceDetailView.as_view(), name='marketplace-detail'),
]
