# ////////////////////////////////////////////////////////////////////
# // name:CLsSentimentData.py                                       //
# // description: Watson Discoveryから特定のワード対する極性          //
# //  (positive/neutoral/negative)を集計してデータ出力する            //
# ////////////////////////////////////////////////////////////////////
import os
import sys
import glob
import datetime
import pandas as pd
import requests
import json
import re

# 個別モジュール
from lib import S3DateCulc as dc
from lib import S3Stats
from lib import S3DBConnect


class MakeSentimentData:
    def __init__(self):
        """コンストラクタ"""
        self.bReturn = False
        self.emsg = ""
        self.NumberOfPositive = 0
        self.NumberOfNeutral = 0
        self.NumberOfNegative = 0

    def AggregateSentimentData(self, NLQ, SSD, SED, USERNAME, PASS):
        """
        description: watsonにSentimentデータをクエリする
        args:
            NLQ:Natural_Language_Query:検索キーワード
            SSD:Search_Start_Date:検索開始日 (YYYYMMDD)
            SED:Search_End_Date:検索終了日  (YYYYMMDD)
            USERNAME: discoveryに照会をかけるためのユーザーID
                        PASS:discoveryに照会をかけるためのパスワード
        return:
            normal: True, Positive数, Neutral数, Negative数
            error: False, Errorメッセージ
        """
        # 変数設定
        VERSION = '2018-08-01'                            # discovery API version
        SEARCH_START_DATE = dc.DateUTime(SSD)       # date for query
        SEARCH_END_DATE = dc.DateUTime(SED)         # date for query
        QUERY_NLQ = NLQ                                   # Query word for Natural Language Query
        URL_NEWS = 'https://gateway.watsonplatform.net/discovery/api/v1/environments/system/collections/news-en/query'

        # curl用パラメータセット
        params = (
            ('version', VERSION),
            ('filter', 'crawl_date>{0}T00:00:00+0900,crawl_date<{1}T23:59:59+0900'.format(SEARCH_START_DATE, SEARCH_END_DATE)),
            ('aggregation', 'term(host).term(enriched_text.sentiment.document.label)'),
            ('natural_language_query', QUERY_NLQ),
        )
        # curl実行
        response = requests.get(
            url=URL_NEWS,
            params=params,
            auth=(USERNAME, PASS)
        )

        if response.status_code != 200:
            self.emsg = '[:ERROR:] STATUS CODE:{0} ERROR MESSAGE:{1}'.format(response.status_code, response.json()['error'])
            return self.bReturn, self.emsg

        # APIからのリターンをjson_dataに格納し、ファイルに保存
        json_data = response.json()
        out_file_name = NLQ + '_' + SED + '.json'
        fp = open(out_file_name, 'w')
        json.dump(json_data, fp)

        # positive/neutral/negativeを集計
        for tmp in json_data['aggregations'][0]['results']:
            for result in tmp['aggregations'][0]['results']:
                if result['key'] == 'positive':
                    self.NumberOfPositive += result['matching_results']
                if result['key'] == 'neutral':
                    self.NumberOfNeutral += result['matching_results']
                if result['key'] == 'negative':
                    self.NumberOfNegative += result['matching_results']
        
        self.bReturn = True
        return self.bReturn, self.NumberOfPositive, self.NumberOfNeutral, self.NumberOfNegative


class MakeSentimentDataLoopAndOutCSV(MakeSentimentData):
    """
    description: MakeSentimentDataの派生クラス
    """
    def __init__(self):
        """
        コンストラクタ: 基底クラスと同じ
        """
        super().__init__()

    def AggregateSentimentData(self, NLQ, SSD, SED, USERNAME, PASS, OUTFILE):
        """
        description: MakeSentimentData.AggregateSentimentDataをオーバーライド。
                   : 日付の差分でループし、CSVにデータを書き出す
        input      : NLQ -> Natural Language Query
                   : SSD -> Sentiment Start day
                   : SED -> Sentiment End day
                   : USENAME -> user name
                   : PASS -> password (plain text)
                   : OUTFILE -> output file name
        return     :
        """
        # 処理用定義
        __STATUS = 0
        __ERROR_MSG = 1
        __POSITIVE = 1
        __NEUTRAL = 2
        __NEGATIVE = 3

        # 期間取得
        duration = dc.DateDiff(SSD, SED)
        # 日付ループ
        for day in range(duration + 1):
            # 照会する日付取得
            query_day = dc.DateAdd(SSD, day)
            # 0埋めした日付文字列を生成
            query_day = str(query_day.year) + '{:02}'.format(query_day.month) + '{:02}'.format(query_day.day)
            # 親クラスのAggregateSentimentDataから出力を受け取る
            sentiments = super().AggregateSentimentData(NLQ, query_day, query_day, USERNAME, PASS)
            print('query_day:{}'.format(query_day))
            # エラーチェック
            if not sentiments[__STATUS]:
                msg = '\n{}'.format(sentiments[__ERROR_MSG])
                # エラー時強制終了
                return 1, msg

            query_day = dc.DateUTime(query_day)
            # dataframeに格納
            senti_data = pd.DataFrame(
                [[NLQ, query_day, sentiments[__POSITIVE], sentiments[__NEUTRAL], sentiments[__NEGATIVE]]],
                columns=['Company Name', 'Date', 'Positive', 'Neutral', 'Negative']
            )
            # 初回はヘッダー含めて新規作成、2回目以降はヘッダー不要で追記
            if day == 0:
                senti_data.to_csv(
                    OUTFILE,
                    index=False,
                )
            else:
                # csvに追記
                senti_data.to_csv(
                    OUTFILE,
                    index=False,
                    mode='a',
                    header=False
                )
        return 0

    def set_sentiment_CSVdata_to_db(self):
        """
        description: センチメントデータを保存したディレクトリから
                   : ファイル名に付与された銘柄コードを抽出し、
                   : csvファイルから対象コードのテーブルにデータをセットする
                   : ※センチメントデータのcsvファイルが保管されているディレクトリがカレントになっている前提
        input      :
        return     : True/False
        """
        TBL_SENTIMENT_NAME = 'Sentiment'
        PJ_NAME = 's3pj'
        MATCH = 0

        rtn = False

        sentiment_csv_files = glob.glob('./*')
        for sentiment_csv_file in sentiment_csv_files:
            file_name = os.path.basename(sentiment_csv_file)
            # ファイル名の先頭4文字を銘柄名として取得する
            regx = '^[0-9]{4}'
            stock_code = re.match(regx, file_name)
            stock_code = stock_code[0]
            # S3StatsCSVクラスを使って株価取得
            # Windowsのファイルパス対策
            file_path = repr(sentiment_csv_file).replace('\\\\', '/')
            Stats = S3Stats.S3StatsCSV(SentiPath=file_name)
            sentiment_data = Stats.getSentiData()

            # ///////////////////////////
            # //　センチメントデータの更新
            # ///////////////////////////
            S3DBConnect.update_or_insert_sentiment_data(
                PJ_NAME,
                TBL_SENTIMENT_NAME,
                sentiment_data,
                stock_code,
            )

        rtn = True

        return rtn
# //////////////////////////////////
# // TEST                         //
# //////////////////////////////////
if __name__ == '__main__':
    import os
    import sys

    NLQ = 'dai ichi life'
    SSD = '20181101'
    SED = '20181130'
    USERNAME = ''  # auth username
    PASS = ''  # auth password
    OUTFILE = 'setiment.csv'
    PJ_ROOT = 'S3_PJ_ROOT'

    # watson discoveryへの認証情報は環境変数から取得する
    # 自分用
    if os.environ['USERNAME'] == 'keisa':
        USERNAME = os.environ['DISCOVERY_USER_NAME']
        PASS = os.environ['DISCOVERY_PASS']
    elif USERNAME == '' or PASS == '':
        print("[:ERROR:] Watson Discoveryに接続するための認証情報が設定されていません")

    # # センチメントデータ取得
    # MakeSentimentData = MakeSentimentDataLoopAndOutCSV()
    # result = MakeSentimentData.AggregateSentimentData(NLQ, SSD, SED, USERNAME, PASS, OUTFILE)

    cwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cwd)
    sentiment_csv_dir = 'data/sentiment'
    os.chdir(sentiment_csv_dir)
    lib_dir = "./lib"
    sys.path.append(lib_dir)

    # センチメントデータでDBを更新
    SentimentCSV = MakeSentimentDataLoopAndOutCSV()
    if SentimentCSV.set_sentiment_CSVdata_to_db():
        print("-----process complete-----")
    else:
        print("[:ERROR:] Something wrang was happen while setting setntiment data to DB")
