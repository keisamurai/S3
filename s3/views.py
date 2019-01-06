from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from s3.models import *
from django_pandas.io import read_frame

from lib import S3Stats
from lib import S3DateCulc
# Create your views here.


def index(request):
    return render(request, 'index.html')


class CommonTemplate(TemplateView):
    a = '1'


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

    def post(self, request, *args, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        code_master = Code_Master.objects.filter(code=kwargs['query_cod'])

    def get(self, request, *args, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        # コードマスタから、照会されているデータだけ抽出する
        code_master = Code_Master.objects.filter(code=kwargs['query_code'])
        stock = Stock.objects.filter(code=kwargs['query_code'])
        sentiment = Sentiment.objects.filter(code=kwargs['query_code'])

        # pandas.DataFrameに変換
        df_stock = read_frame(stock)
        df_sentiment = read_frame(sentiment)
        # id列を削除 ※djangoのquerysetからdfに変換する際に付与されるが、邪魔なので削除する
        df_stock = df_stock.drop('id', axis=1)
        df_sentiment = df_sentiment.drop('id', axis=1)

        # S3Stats準備
        stats = S3Stats.S3Stats()

        today = "2018-12-05"
        one_month_before = S3DateCulc.DateConv(S3DateCulc.month_delta(today, month=-1), 1)
        one_week_before = S3DateCulc.DateConv(S3DateCulc.month_delta(today, week=-1), 1)

        # montlyとweeklyの株価を取得する。
        monthly_stock = stats.df_filter(df_stock, start_day=one_month_before, end_day=today)
        weekly_stock = stats.df_filter(df_stock, start_day=one_week_before, end_day=today)

        # 株価とセンチメントデータの統計情報を取得
        stock_describe = df_stock.describe().round(1)
        stock_monthly_describe = monthly_stock.describe().round(1)
        stock_weekly_describe = weekly_stock.describe().round(1)
        sentiment_describe = df_sentiment.describe().round(1)

        # 株価とセンチメントデータの変化率データ取得
        merged_data = stats.merge_ss(df_stock, df_sentiment)
        change_rate = stats.change_rate_stock_data(merged_data)
        corr = change_rate.corr()

        # 範囲指定用の数値
        upper_limit = -0.01
        lower_limit = ""
        # 範囲指定をする対象の列名を指定
        range_target_label = ['opening']

        # 1日シフトしたデータを取得
        shift_list = ['opening', 'high', 'low', 'closing', 'volume', 'adjustment']
        merged_data_shift = stats.shift_data(merged_data, shift_list)
        change_rate_shift = stats.change_rate_stock_data(
            merged_data_shift,
            upper_limit=upper_limit,
            lower_limit=lower_limit,
            range_target_label=range_target_label,
        )
        corr_shift = change_rate_shift.corr()

        # 変化率10%以上のデータを取得
        change_rate_10_percent = stats.change_rate_stock_data(
                merged_data,
                upper_limit=upper_limit,
                lower_limit=lower_limit,
                range_target_label=range_target_label,
            )
        corr_10_percent = change_rate_10_percent.corr()

        # 日本語名を取得
        for cd in code_master:
            context['jp_name'] = cd.jp_name

        # ========================
        # context 定義
        # ========================
        context['stock'] = stock
        context['monthly_stock'] = monthly_stock
        context['stock_monthly_describe'] = stock_monthly_describe
        context['stock_weekly_describe'] = stock_weekly_describe
        context['weekly_stock'] = weekly_stock
        context['sentiment'] = sentiment
        context['stock_describe'] = stock_describe
        context['stock_describe_columns'] = stock_describe.columns
        context['sentiment_describe'] = sentiment_describe
        context['sentiment_describe_columns'] = sentiment_describe.columns
        context['query_code'] = kwargs['query_code']
        context['change_rate'] = change_rate
        context['corr'] = corr
        context['change_rate_shift'] = change_rate_shift
        context['corr_shift'] = corr_shift
        context['change_rate_10'] = change_rate_10_percent
        context['corr_10'] = corr_10_percent

        # -------------------
        # stock/sentiment統計値定義
        # -------------------
        # dictionary型でデータを取得
        dict_stock_describe = stock_describe.to_dict()
        dict_sentiment_describe = sentiment_describe.to_dict()

        stock_describe_column = stock_describe.columns
        stock_describe_index = stock_describe.index
        sentiment_describe_column = sentiment_describe.columns
        sentiment_describe_index = sentiment_describe.index

        # dictionaryのデータを行ごとのデータに入れなおす(stock)
        for row in stock_describe_index:
            tmp_list = []
            for col in stock_describe_column:
                tmp_list.append(dict_stock_describe[col][row])
            cn = 'st_desc_' + row
            context[cn] = tmp_list

        # dictionaryのデータを行ごとのデータに入れなおす(sentiment)
        for row in sentiment_describe_index:
            tmp_list = []
            for col in sentiment_describe_column:
                tmp_list.append(dict_sentiment_describe[col][row])
            cn = 'se_desc_' + row
            context[cn] = tmp_list

        # -------------------
        # 各種変化率定義
        # -------------------
        for col_name in change_rate:
            # ex. cn = cr_opening
            # ※DataFrameを単純にforに使うと列名(str)を取得する
            cn = 'cr_' + col_name
            context[cn] = change_rate[col_name]
        for corr_col_name in corr:
            cn = 'corr_' + corr_col_name
            context[cn] = corr.loc[corr_col_name].round(3)

        for col_name in change_rate_shift:
            cn = 'cr_shift_' + col_name
            context[cn] = change_rate_shift[col_name]
        for corr_col_name in corr_shift:
            cn = 'corr_shift_' + corr_col_name
            context[cn] = corr_shift.loc[corr_col_name].round(3)

        for col_name in change_rate_10_percent:
            cn = 'cr_10_' + col_name
            context[cn] = change_rate_10_percent[col_name]
        for corr_col_name in corr_10_percent:
            cn = 'corr_10_' + corr_col_name
            context[cn] = corr_10_percent.loc[corr_col_name].round(3)

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


class SettingsView(TemplateView):
    template_name = "settings.html"

    def get(self, request, *args, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)

        return render(self.request, self.template_name, context)
