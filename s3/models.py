from django.db import models

# Create your models here.
class Code_Master(models.Model):
    """
    description: 管理対象銘柄のマスタ
    """
    # 銘柄コード
    code = models.CharField(max_length=4)
    # 会社名(日本語)
    jp_name = models.CharField(max_length=128)
    # 会社名(英語)
    en_name = models.CharField(max_length=128)

class Stock(models.Model):
    """
    description: 管理対象銘柄の株価データ
    """
    
    BIZ_DAY = 0 #営業日
    NON_BIZ_DAY = 1 #非営業日

    # 銘柄コード
    code = models.CharField(max_length=4)
    # データ日付
    date = models.CharField(max_length=10)
    # 営業日or非営業日
    # biz_day = models.IntegerField(editable=False)
    # 開始値
    opening = models.FloatField()
    # 高値
    high = models.FloatField()
    # 安値
    low = models.FloatField()
    # 終値
    closing = models.FloatField()
    # 終値
    volume = models.IntegerField()
    # 調整値
    adjustment = models.FloatField()

class Sentiment(models.Model):
    """
    description: 管理対象銘柄のセンチメントデータ
    """
    #銘柄コード
    code = models.CharField(max_length=4)
    #会社名
    name = models.CharField(max_length=128)
    # データ日付
    date = models.DateField()
    # positive
    positive = models.IntegerField()
    # neutral
    neutral = models.IntegerField()
    # negative
    negative = models.IntegerField()
