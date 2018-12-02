# ///////////////////////////////////////
# // name: stockdata_download.py
# // description: ウェブページから株価情報を
# //   ダウンロードする
# // conditions:
# //   1.スクリプト配置フォルダに
# //   銘柄情報のcsvファイルが配置されていること
# //   2.chromeのbrowserdriverがインストール
# //   されていること
# ///////////////////////////////////////
import sys
import os
import pandas

from selenium import webdriver

from lib import S3DBConnect
from lib import S3Stats
from lib import S3Util


def DLStockData(code_master, out_dir):
    """
    description : 株価データをダウンロードする
    input       : code_master -> 銘柄コード(Iterator)
                : out_dir -> 出力先のディレクトリ
    output      : 株価データ(csv)
    return      : True/False
    """
    rtn = True

    # ダウンロード先ディレクトリを設定
    dl_dir = os.path.abspath(out_dir)
    print(dl_dir)

    # 環境変数からchromedriverのパスを取得取得
    environ = os.environ
    CHROME_DRIVER_PATH = environ['CHROME_DRIVER_PATH']
    URL_BASE = "https://kabuoji3.com/stock/"
    URL_YEAR = '2018'
    WAIT_SEC = 10

    try:
        # //////////////////////////////////
        # // chrome driver
        # //////////////////////////////////
        chop = webdriver.ChromeOptions()
        prefs = {"download.default_directory": dl_dir}   # ダウンロード先設定
        chop.add_experimental_option("prefs", prefs)
        # chop.add_argument('--ignore-certificate-errors')  # SSL対策
        # chop.add_argument('--headless') # headless 設定
        # chop.add_argument('--disable-gpu') # gpu error 対策
        # chop.add_argument('--window-size=1024,1000')
        # chop.add_argument('--disable-extensions')
        # chromeドライバ取得
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH,
                                  chrome_options=chop)

        for data in code_master:
            # url作成
            url = URL_BASE + str(data.code) + '/' + URL_YEAR + '/'
            driver.get(url)
            driver.implicitly_wait(WAIT_SEC)
            # ダウンロードページへ
            driver.find_element_by_xpath(
                '//*[@id="base_box"]/div/div[3]/form/button'
                ).click()
            driver.implicitly_wait(WAIT_SEC)
            # ダウンロードボタンをクリック
            driver.find_element_by_xpath(
                '//*[@id="base_box"]/div/div[3]/form/button'
                ).click()
            driver.implicitly_wait(WAIT_SEC)

        # クローズ処理
        driver.close()
    except:
        rtn = False

    return rtn


def UPDorINSStockData(input_dir):
    """
    description : csvから株価データを取得し、Stockテーブルに存在すればUPDATE、
                : 存在しなければINSERTする
    input       : input_dir -> 株価データ(csv)の保管ディレクトリ
    output      :
    return      : True/False
    """
    import re
    import glob

    TBL_STOCK_NAME = 'Stock'
    PJ_NAME = 's3pj'
    MATCH = 0

    rtn = False
    # inputフォルダのファイルを取得
    if S3Util.add_dot_dir_path(input_dir):
        input_dir = S3Util.add_dot_dir_path(input_dir)
    else:
        return rtn

    glob_dir = input_dir + '/*'
    files = glob.glob(glob_dir)
    for file_path in files:
        # ファイル名の先頭4文字を銘柄コードとして取得
        file_name = os.path.basename(file_path)
        regx = '^[0-9]{4}'
        stock_code = re.match(regx, file_name)
        stock_code = stock_code[0]
        # S3StatsCSVクラスを使って株価取得
        # Windowsのファイルパス対策
        file_path = repr(file_path).replace('\\\\', '/')
        Stats = S3Stats.S3StatsCSV(StockPath=file_name)
        stock_data = Stats.getStockData(path=input_dir)

        # ////////////////
        # // 株価データ更新
        # ////////////////
        S3DBConnect.update_or_insert_stock_data(
            PJ_NAME,
            TBL_STOCK_NAME,
            stock_data,
            stock_code
            )

    rtn = True

    return rtn

# //////////////////////////////
# // main process
# //////////////////////////////
if __name__ == '__main__':
    PJ_NAME = 's3pj'
    TBL_CODE_MASTER_NAME = 'Code_Master'
    TBL_STOCK_NAME = 'Stock'
    OUT_DIR = './data/stock'
    PJ_ROOT = 'S3_PJ_ROOT'

    cwd = os.path.dirname(os.path.abspath(__file__))
    os.chdir(cwd)
    # libをpathに追加
    lib_dir = "./lib/"
    sys.path.append(lib_dir)

    # ダウンロード先のディレクトリ
    out_dir = '{}'.format(OUT_DIR)

    # dbに接続してテーブルのデータを受け取る
    tbl_data = S3DBConnect.get_db_object(PJ_NAME, TBL_CODE_MASTER_NAME)
    if len(tbl_data) == 0:
        print("[:ERROR:] Something wrong was happen while getting code_master data")

    # 銘柄コードをもとにデータをダウンロードする
    # if not DLStockData(tbl_data, out_dir):
    #     print('[:ERROR:] Something wrong was happen while stock data downloading')

    # 株価データを更新する
    if not UPDorINSStockData(out_dir):
        print('[:ERROR:] Something wrong was happen while stock data updating')

    # csvファイルを削除する
    # rm_path = cwd + "/data/stock/"
    # S3Util.del_all_files_in_dir(rm_path)
