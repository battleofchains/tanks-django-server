from django.contrib import admin

from .models import Offer, Tank


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'amount', 'price', 'amount_sold', 'is_active')

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(OfferAdmin, self).get_form(request, obj, change, **kwargs)
        form.base_fields['base_tank'].queryset = Tank.objects.filter(basic_free_tank=True)
        return form
