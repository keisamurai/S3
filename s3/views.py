from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from s3.models import *
from django_pandas.io import read_frame

from lib import S3Stats
# Create your views here.


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get(self, request, *args, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        # コードマスタから、照会されているデータだけ抽出する
        code_master = Code_Master.objects.filter(code=9984)
        # 株価データから、照会されているデータだけ抽出する
        stock = Stock.objects.filter(code=9984, date__gte='2018-11-01')  # DBからオブジェクトを取得

        # 日本語名を取得
        for cd in code_master:
            context['jp_name'] = cd.jp_name

        context['stock'] = stock
        context['query_code'] = 9984
        return render(self.request, self.template_name, context)


class MasterListView(TemplateView):
    template_name = "code_master.html"

    def get(self, request, *args, **kwargs):
        context = super(MasterListView, self).get_context_data(**kwargs)

        code_master = Code_Master.objects.all()  # DBからオブジェクトを取得
        # workers = Worker.objects.filter(person__sex=Person.MAN)
        context['code_master'] = code_master  # 別の入れ物に入れる

        return render(self.request, self.template_name, context)


class DataListView(TemplateView):
    template_name = "data_list.html"

    def get(self, request, *args, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        # コードマスタから、照会されているデータだけ抽出する
        code_master = Code_Master.objects.filter(code=kwargs['query_code'])
        stock = Stock.objects.filter(code=kwargs['query_code'])
        sentiment = Sentiment.objects.filter(code=kwargs['query_code'])

        # pandas.DataFrameに変換
        df_stock = read_frame(stock)
        df_sentiment = read_frame(sentiment)
        # S3Stats準備
        stats = S3Stats.S3Stats()
        # 株価とセンチメントデータの変化率データ取得
        merged_data = stats.mergeSS(df_stock, df_sentiment)
        change_rate = stats.ChangeRateData(merged_data)
        corr = change_rate.corr()

        # 日本語名を取得
        for cd in code_master:
            context['jp_name'] = cd.jp_name

        # context 定義
        context['stock'] = stock
        context['sentiment'] = sentiment
        context['query_code'] = kwargs['query_code']
        context['change_rate'] = change_rate
        context['corr'] = corr
        for col_name in change_rate:
            # ex. cn = cr_opening
            # ※DataFrameを単純にforに使うと列名(str)を取得する
            cn = 'cr_' + col_name
            context[cn] = change_rate[col_name]

        return render(self.request, self.template_name, context)


class StockListFullView(TemplateView):
    template_name = "stock_list_full.html"

    def get(self, request, *args, **kwargs):
        context = super(StockListFullView, self).get_context_data(**kwargs)
        stock = Stock.objects.all()

        context['stock'] = stock

        return render(self.request, self.template_name, context)


class SentimentListView(TemplateView):
    template_name = "sentiment_list.html"

    def get(self, request, *args, **kwargs):
        context = super(SentimentListView, self).get_context_data(**kwargs)

        sentiment = Sentiment.objects.all()  # DBからオブジェクトを取得
        # workers = Worker.objects.filter(person__sex=Person.MAN)
        context['sentiment'] = sentiment  # 別の入れ物に入れる

        return render(self.request, self.template_name, context)
