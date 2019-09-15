from django.contrib import admin

from .models import User_Master, Vital, Sentiment
# Register your models here.
admin.site.register(User_Master)
admin.site.register(Vital)
admin.site.register(Sentiment)
