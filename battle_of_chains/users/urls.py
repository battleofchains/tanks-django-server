from django.urls import path

from battle_of_chains.users.views import HangarDetailView, HangarView, user_redirect_view, user_update_view

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("hangar/", HangarView.as_view(), name='hangar'),
    path("hangar/<int:pk>/", HangarDetailView.as_view(), name='hangar-detail'),
]
