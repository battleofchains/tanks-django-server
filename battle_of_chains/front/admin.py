from solo.admin import SingletonModelAdmin
from .models import IndexPage, GamePage
from django.contrib import admin


@admin.register(IndexPage)
class IndexPageAdmin(SingletonModelAdmin):
    readonly_fields = ('updated',)


@admin.register(GamePage)
class GamePageAdmin(SingletonModelAdmin):
    readonly_fields = ('updated',)
