#////////////////////////////////////////////////////////////////////
#// name:CLsSentimentData.py                                       //
#// description: Watson Discoveryから特定のワード対する極性          //
#//  (positive/neutoral/negative)を集計してデータ出力する            //
#////////////////////////////////////////////////////////////////////
import datetime
import pandas as pd
import requests
import json

# 個別モジュール
import S3DateCulc as dc

class MakeSentimentData:
    def __init__(self):
        """コンストラクタ"""
        self.bReturn=False
        self.emsg=""
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
        VERSION='2018-08-01'                            # discovery API version
        SEARCH_START_DATE=dc.DateUTime(SSD)       # date for query
        SEARCH_END_DATE=dc.DateUTime(SED)         # date for query
        QUERY_NLQ=NLQ                                   # Query word for Natural Language Query
        URL_NEWS='https://gateway.watsonplatform.net/discovery/api/v1/environments/system/collections/news-en/query'

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
        # エラーチェック
        if response.status_code != 200:
            self.emsg = '[:ERROR:] STATUS CODE:{0} ERROR MESSAGE:{1}'.format(response.status_code, response.json()['error'])
            return self.bReturn, self.emsg

        # APIからのリターンをjson_dataに格納 
        json_data = response.json()

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
                     日付の差分でループし、CSVにデータを書き出す
        """
        # 処理用定義
        __STATUS=0
        __ERROR_MSG=1
        __POSITIVE=1
        __NEUTRAL=2
        __NEGATIVE=3

        # 期間取得
        duration = dc.DateDiff(SSD, SED)
        # 日付ループ
        for day in range(duration + 1):
            # 照会する日付取得
            query_day = dc.DateAdd(SSD, day)
            # 0埋めした日付文字列を生成
            query_day = str(query_day.year) + '{:02}'.format(query_day.month) + '{:02}'.format(query_day.day)
            # 親クラスのAggregateSentimentDataから出力を受け取る
            sentiments = super().AggregateSentimentData(NLQ, SSD, SED, USERNAME, PASS)
            # エラーチェック
            if not sentiments[__STATUS]:
                msg = '\n{}'.format(sentiments[__ERROR_MSG])
                # エラー時強制終了  
                return 1, msg 
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

#//////////////////////////////////
#// TEST                         //
#//////////////////////////////////
if __name__ == '__main__':
    NLQ='dai-ichi-life'
    SSD='20181011'
    SED='20181012'
    USERNAME= ''# auth username
    PASS=''  # auth password
    OUTFILE=''

    MakeSentimentData = MakeSentimentDataLoopAndOutCSV()
    result = MakeSentimentData.AggregateSentimentData(NLQ, SSD, SED, USERNAME, PASS, OUTFILE)

    # check result
    if result[0] == 0:
        print('---process complete--')
    else:
        print('{}'.format(result[1]))