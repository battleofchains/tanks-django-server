from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import GamePage, IndexPage


@admin.register(IndexPage)
class IndexPageAdmin(SingletonModelAdmin):
    readonly_fields = ('updated',)


@admin.register(GamePage)
class GamePageAdmin(SingletonModelAdmin):
    readonly_fields = ('updated',)
