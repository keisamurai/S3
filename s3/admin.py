from django.contrib import admin

from .models import Code_Master, Stock, Sentiment
# Register your models here.
admin.site.register(Code_Master)
admin.site.register(Stock)
admin.site.register(Sentiment)