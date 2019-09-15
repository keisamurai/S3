import sys
import os
import django

import datetime
import pandas as pd

def setting_Django():
    sys.path.append("s3pj")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "s3pj.settings")

    django.setup()

    from s3.models import User_Master, Vital, Sentiment

    print("connect OK")
    c = Vital.objects.all()
    print(c)

    """
    銘柄一覧の反映
    """
    # スクリプトディレクトリに移動
    cws = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cws)
    data_path = './data/master/master.csv'
    # 株価データ取得
    code_master = pd.read_csv(
        data_path,
        header=None,
        names=['code', 'jp_name', 'en_name']
    )

    for i in range(len(code_master)):
        User_Master.objects.create(
           code=code_master['code'][i],
           jp_name=code_master['jp_name'][i],
           en_name=code_master['en_name'][i],
        )
        i +=1

    """
    センチメントデータの反映
    """

if __name__ == '__main__':
    setting_Django()