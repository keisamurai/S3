import sys
import os
import django

import datetime
import pandas as pd

def setting_Django():
    sys.path.append("s3pj")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s3pj.settings")

    django.setup()

    from s3.models import Code_Master, Stock, Sentiment

    print("connect OK")
    c = Stock.objects.all()
    print(c)

    """
    株価データの反映
    """
    # スクリプトディレクトリに移動
    cws = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cws)
    data_path = './data/stock/9984_2018.csv'
    # 株価データ取得
    stock_data = pd.read_csv(
        data_path,
        header=1,
        encoding='ms932',
        names=['date', 'opening', 'high', 'low', 'closing', 'volume', 'adjustment']
    )

    for i in range(len(stock_data)):
        Stock.objects.create(
           code='9984',
           date=stock_data['date'][i],
           opening=stock_data['opening'][i],
           high=stock_data['high'][i],
           low=stock_data['low'][i],
           closing=stock_data['closing'][i],
           volume=stock_data['volume'][i],
           adjustment=stock_data['adjustment'][i],
        )
        i +=1

    """
    センチメントデータの反映
    """

if __name__ == '__main__':
    setting_Django()