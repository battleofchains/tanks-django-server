from django.contrib import admin

from battle_of_chains.utils.mixins import AdminNoChangeMixin

from .models import Room


@admin.register(Room)
class RoomAdmin(AdminNoChangeMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'users_count')
    readonly_fields = ('users',)

    def users_count(self, obj):
        return obj.users.count()
