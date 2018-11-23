from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from s3.models import *
# Create your views here.

class StockListView(TemplateView):
    template_name = "stock_list.html"

    def get(self, request, *args, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)

        stock = Stock.objects.all() # DBからオブジェクトを取得
        # workers = Worker.objects.filter(person__sex=Person.MAN)
        context['stock'] = stock # 別の入れ物に入れる

        return render(self.request, self.template_name, context)
