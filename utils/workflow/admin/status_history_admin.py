# -*- coding: utf-8 -*-

from django.contrib import admin

class StatusHistoryAdmin(admin.ModelAdmin):
    #
    # In line admin
    #
    list_display = ( 'model_repr', 'status', 'timestamp', 'actor', 'current' )
    search_fields = [ '^model__uuid' ]

    def model_repr(self, obj):
        return str(obj.model)
