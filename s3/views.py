from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from s3.models import *
# Create your views here.


class MasterListView(TemplateView):
    template_name = "code_master.html"

    def get(self, request, *args, **kwargs):
        context = super(MasterListView, self).get_context_data(**kwargs)

        code_master = Code_Master.objects.all()  # DBからオブジェクトを取得
        # workers = Worker.objects.filter(person__sex=Person.MAN)
        context['code_master'] = code_master  # 別の入れ物に入れる

        return render(self.request, self.template_name, context)


class StockListView(TemplateView):
    template_name = "stock_list.html"

    def get(self, request, *args, **kwargs):
        context = super(StockListView, self).get_context_data(**kwargs)
        # コードマスタから、照会されているデータだけ抽出する
        code_master = Code_Master.objects.filter(code=kwargs['query_code'])
        # 株価データから、照会されているデータだけ抽出する
        stock = Stock.objects.filter(code=kwargs['query_code']) # DBからオブジェクトを取得

        # 日本語名を取得
        for cd in code_master:
            context['jp_name'] = cd.jp_name
        context['stock'] = stock
        context['query_code'] = kwargs['query_code']
        return render(self.request, self.template_name, context)


class SentimentListView(TemplateView):
    template_name = "sentiment_list.html"

    def get(self, request, *args, **kwargs):
        context = super(SentimentListView, self).get_context_data(**kwargs)

        sentiment = Sentiment.objects.all()  # DBからオブジェクトを取得
        # workers = Worker.objects.filter(person__sex=Person.MAN)
        context['sentiment'] = sentiment  # 別の入れ物に入れる

        return render(self.request, self.template_name, context)
