# ///////////////////////////////////////////////////////
# // name         : S3DBConnect.py
# // description　: djangoのデータベースにアクセスし、オブジェクト
# //              : を返す
# ///////////////////////////////////////////////////////
import sys
import os
import django


def get_db_object(pjname, tbl_name):
    """
    description : djangoのデータベースにアクセスし、オブジェクトを返す
    input       : pjname -> PJ名(s3pj)
                : tbl_name -> テーブル名
    output      : obj -> 要求のあったオブジェクト
    """
    TBL_CODE_MASTER_NAME = "Code_Master"
    TBL_STOCK_NAME = "Stock"
    TBL_SENTIMENT_NAME = "Sentiment"

    sys.path.append(pjname)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(pjname))
    os.chdir(os.environ['S3_PJ_ROOT'])

    django.setup()

    # fromでエラーで表示されるが、問題なく実行できる
    from s3.models import Code_Master, Stock, Sentiment

    if tbl_name == TBL_CODE_MASTER_NAME:
        try:
            tbl = Code_Master.objects.all()
        except:
            print("[:ERROR:] getting table data failed")
            return
    elif tbl_name == TBL_STOCK_NAME:
        try:
            tbl = Stock.objects.all()
        except:
            print("[:ERROR:] getting table data failed")
            return
    elif tbl_name == TBL_SENTIMENT_NAME:
        try:
            tbl = Sentiment.objects.all()
        except:
            print("[:ERROR:] getting table data failed")
            return

    else:
        print("[:ERROR:] getting table data failed")
        return

    return tbl


def update_or_insert_stock_data(pjname, tbl_name, stock_data, stock_code):
    """
    description : 株価データのテーブルにアクセスし、データが存在すればUPDATE,
                : データが存在しなければINSERTする
    input       : pjname -> PJ名(s3pj)
                : tbl_name -> テーブル名
                : stock_data -> 株価データ
                : stock_code -> 対象株価データの銘柄コード
    output      : true/false
    """
    TBL_STOCK_NAME = "Stock"

    rtn = False

    sys.path.append(pjname)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{}.settings".format(pjname))
    os.chdir(os.environ['S3_PJ_ROOT'])

    django.setup()

    from s3.models import Stock

    if tbl_name == TBL_STOCK_NAME:
        try:
            for i in range(len(stock_data)):
                rtn = Stock.objects.update_or_create(
                    code=stock_code,
                    date=stock_data['date'][i],
                    opening=stock_data['opening'][i],
                    high=stock_data['high'][i],
                    low=stock_data['low'][i],
                    closing=stock_data['closing'][i],
                    volume=stock_data['volume'][i],
                    adjustment=stock_data['adjustment'][i],
                )
        except:
            print("[:ERROR:] getting table data failed")
            return rtn
    else:
        print("[:ERROR:] getting table data failed")
        return rtn

    return rtn
