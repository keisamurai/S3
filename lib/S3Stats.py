# ////////////////////////////////////
# // StockAndSentimentSystem:Stats
# //   ///////   ///////
# //  ///__  // ///__  //
# // | //  \__/|__/  \ //
# // |  //////    ///////
# //  \____  //  |___  //
# //  ///  \ // ///  \ //
# // |  ///////|  ///////
# //  \______/  \______/
# ////////////////////////////////////
import os
import sys
import pandas as pd
import traceback
import glob

# 個別作成モジュール
from lib import S3DateCulc as dc


class S3Stats:

    def __init__(self, StockPath="", SentiPath=""):
        """Constructor"""
        self.StockPath = StockPath
        self.SentiPath = SentiPath
        self.emsg = ""
        self.POS_STATUS = 0
        self.POS_MSG = 1
        self.SUCCESS_STATUS = True
        self.ERROR_STATUS = False

    def __del__(self):
        """Deconstructor"""
        pass

    def set_stock_path(self, StockPath):
        """
        description: 株価データのパスをセットする
        """
        self.StockPath = StockPath

    def get_stock_path(self):
        """
        description: 株価データのパスを返す
        """
        return self.StockPath

    def set_senti_path(self, SentiPath):
        """
        description: センチメントデータのパスをセットする
        """
        self.SentiPath = SentiPath

    def get_senti_path(self):
        """
        description: センチメントデータのパスを返す
        """
        return self.set_senti_path

    def check_path(self):
        """
        description: センチメントデータと株価データの存在確認（オーバーライド前提）
        """
        pass

    def get_stock_and_senti(self, TargetCode):
        """
        description: センチメントデータと株価データ取得（オーバーライド前提）
        """
        pass

    def merge_ss(self, stock_data, senti_data):
        """
        description : 株価とセンチメントデータを統合する
        args        : senti_data -> センチメントデータ
                    : stock_data -> 株価データ
        return      : merged_data  -> センチメントデータと株価データの統合データ
        # 基底クラスにもっていっていいかも
        """

        # 株価データとセンチメントデータのcode列が重複してmerge時に
        # 強制的に列名がcode_xとcode_yになってしまうので事前にcode列を一方から削除
        senti_data = senti_data.drop('code', axis='columns')

        merged_data = pd.merge(stock_data, senti_data, on='date')
        return merged_data

    def change_rate_data(self, merged_data):
        """
        description : 統合されたデータを変化率のデータに変換する
                    :   opening -> 開始値
                        closing -> 終値
                        positive -> positive 数
                        neutral -> neutral 数
                        negative -> negative 数
        args        : merged_data -> センチメントデータと株価データの統合データ
        return      : changerate_data -> 変化率のデータ
        """
        # 必要な列を取得する
        needed_data = merged_data.loc[:, ['opening', 'closing', 'positive', 'neutral', 'negative']]
        changerate_data = needed_data.pct_change()

        # pct_change()を利用することで、時点0のデータがNaNになるため、
        # 0で穴埋めする
        changerate_data = changerate_data.fillna(0)

        return changerate_data

    def shift_data(self, data, shift_list, shift=-1):
        """
        description : dataを与えられた数値分ずらす
                    :  ※株価データを一日前倒しするために利用する想定
        args        : data -> DataFrame
                    : shift_list -> ずらす対象のリスト
                    : shift -> ずらす数値
        return      : shiftedData -> ずらした後のデータ
        """
        tmp = data.loc[:, shift_list].shift(shift)
        data.loc[:, shift_list] = tmp
        shiftedData = data.loc[:, shift_list]

        return shiftedData

    def find_stock_na_date(self, stock_data):
        """
        description: 株価データ(dataframe)の欠損日付(N/ADate)を取得する
        output: 欠損日付(list)
        """
        na_list = []
        # stock_dataの初日(YYYY-MM-DD形式)と最終日(YYYY-MM-DD形式)を取得する
        start = stock_data['date'][0]  # 初日
        end = stock_data['date'][len(stock_data['date']) - 1]  # 最終日
        # start と end　の差分を取得する
        diff = dc.DateDiff(start, end)
        if diff <= 2:  # 差分が2以下の場合、欠損日付はない。
            return na_list
        else:  # 欠損日を確認して、listに追加する
            # startとendから日付のリストを生成
            day_list = dc.DateList(dc.DateUTime(start), dc.DateUTime(end))

            # -------------------------------------------------------
            # 機械的に生成した全日日付(day_list)と、営業日データ(stock_data['date'])から、
            # # 一致しない日付がNAと判断する
            # @無駄に回りすぎる(len(day_list) * len(stock_data['date']))
            # for allday in day_list:
            #     for bizday in stock_data['date']:
            #         if allday != bizday:
            #             # bizdayに存在しないalldayの日付をna_listに追加する
            #             na_list.append(allday)
            # -------------------------------------------------------

            # 機械的に生成した全日日付(day_list)と、営業日データ(stock_data['date'])から、
            # 一致しない日付がNAと判断する
            i = 0
            j = 0
            for all_day in range(len(day_list)):
                if day_list[i] == stock_data['date'][j]:
                    i += 1
                    j += 1
                else:  # day_list[i]がstock_data['data'][j]に存在しない場合、na_listに追加し、iだけ進める
                    na_list.append(day_list[i])
                    i += 1

            return na_list

    def comp_stock_na(self, stock_data, na_list, round_digit=""):
        """
        description:株価データの欠損値を線形補完する
        input      :stock_data -> 株価データ(df)
                   :na_list    -> 欠損している日付のlist
                   :round_digit -> 欠損値を四捨五入する際の桁
                   :           (ex.12.44はround_digit=1のとき、12.4として四捨五入される)
        output     :(success) stock_data -> 欠損値を補完した株価データ
                   :(fail) False
                   :(fail) emsg
        assumption :stock_dataの最初と最後の日付にはデータが入っている想定
        """
        # 最初かどうかを見るフラグ
        fflg = 0
        # ------------------------------
        # na_list からDataFrameを作成
        # ------------------------------
        for date in na_list:
            # 日付以外を初期化
            work_df_tmp = pd.DataFrame(
                    [[date, 0, 0, 0, 0, 0, 0]],
                    columns=['date', 'opening', 'high', 'low', 'closing', 'volume', 'adjustment']
                )
            if fflg == 0:
                work_df = work_df_tmp
                fflg = 1
            else:
                # 2回目以降のループではwork_dfに追加
                work_df = work_df.append(work_df_tmp)

        # ------------------------------
        # na_listを追加したstock_dataを初期化
        # ------------------------------
        # na_df を stock_dataに追加する
        stock_data = stock_data.append(work_df)
        # stock_dataを日付でソートする
        stock_data = stock_data.sort_values('date')
        # indexの初期化
        stock_data = stock_data.reset_index(drop=True)

        # ------------------------------
        # na_listから価格がゼロの日付の価格を線形補完
        # ------------------------------
        na_work_list = []
        na_work_idx = 0
        target_label = ['opening', 'high', 'low', 'closing', 'volume', 'adjustment']
        for na_day in na_list:
            # na_work_listの最初の要素について、na_dayをna_work_listに追加して、イテレータを進める
            if (na_work_idx == 0):
                na_work_idx += 1
                na_work_list.append(na_day)
                continue

            # na_listの最後の要素について、補完処理よりも先にna_dayをna_work_listに追加する
            if na_day == na_list[len(na_list) - 1]:
                na_work_list.append(na_day)

            # na_work_listの最新の値と、na_dayの一日前が一致しない場合、補完処理にna_worK_listを渡す
            if na_work_list[len(na_work_list) - 1] != dc.DateConv(dc.DateAdd(dc.CharConv(na_day, mode=1), -1), mode=1):
                # -----------------------------
                # 補完処理
                # -----------------------------
                # na_work_list[0]の前日
                pre_na_day = dc.DateAdd(dc.CharConv(na_work_list[0], mode=1), -1)
                # na_work_list[len(na_work_list) - 1] の翌日
                next_na_day = dc.DateAdd(dc.CharConv(na_work_list[len(na_work_list) - 1], mode=1), 1)
                # 線形補完の始点の日付(YYYY-MM-DD)
                day_x0 = dc.DateConv(pre_na_day, mode=1)
                # 線形補完の終点の日付(YYYY-MM-DD)
                day_x1 = dc.DateConv(next_na_day, mode=1)

                # na_work_list でループ
                for day_x in na_work_list:
                    for label in target_label:
                        # 線形補完の始点の日付のインデックス
                        x0 = stock_data[stock_data['date'] == day_x0].index.values
                        # 線形補完の終点の日付のインデックス
                        x1 = stock_data[stock_data['date'] == day_x1].index.values
                        y0 = stock_data[stock_data['date'] == day_x0][label]
                        y1 = stock_data[stock_data['date'] == day_x1][label]
                        x = stock_data[stock_data['date'] == day_x].index.values

                        # 線形補完に必要な数値にアクセス
                        x0 = x0[0]
                        x1 = x1[0]
                        y0 = y0[y0.index.values[0]]
                        y1 = y1[y1.index.values[0]]
                        x = x[0]
                        y = self.calc_lerp(x0, x1, y0, y1, x)
                        
                        # 四捨五入する場合は、インプットに応じて丸め処理
                        if not round_digit == "":
                            y = round(y, round_digit)

                        # 値を代入
                        stock_data.loc[stock_data['date'] == day_x, label] = y
                # -----------------------------
                # 初期化
                # -----------------------------
                na_work_list = []
                na_work_list.append(na_day)

            # na_work_listの最新の値と、na_dayの一日前が一致する場合
            else:
                na_work_list.append(na_day)

        return stock_data

    def calc_lerp(self, x0, x1, y0, y1, x):
        """
        description : 線形補完(Linear interpolation)を計算する
        args        : x0 -> 始点のx軸値
                    : x1 -> 終点のx軸値
                    : y0 -> 始点のy軸値
                    : y1 -> 終点のy軸値
                    : x -> 補完する値のx軸値
        return      : y -> 補完する値のy軸値
        """
        # 初期化
        y = 0
        try:
            y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        except ZeroDivisionError:
            # ゼロ割の時はFalseを返す
            return False

        return y

    def stock_MAI(self, stock_data):
        """
        description: 株価データから移動平均(Moving Average)を求める
        # 後で実装
        """
        pass


class S3StatsCSV(S3Stats):
    """CSVデータ用のS3Statsの派生クラス"""
    def __init__(self, StockPath="", SentiPath=""):
        """Constructor"""
        super().__init__(StockPath, SentiPath)

    def check_path(self, mode):
        """
        description : センチメントデータ(CSV)と株価データ(CSV)の存在確認
        input       : mode -> 実行モード
                    :     0 ->  株価データのみチェック
                    :     1 ->  センチメントデータのみチェック
                    :     2 ->  株価データ、センチメントデータ両方チェック
        """
        if mode == 0 or mode == 2:
            if not os.path.exists(self.StockPath):
                self.emsg = '[:ERROR:]File not exists:{}'.format(self.StockPath)
                return self.ERROR_STATUS, self.emsg
        if mode == 1 or mode == 2:
            if not os.path.exists(self.SentiPath):
                self.emsg = '[:ERROR:]File not exists:{}'.format(self.SentiPath)
                return self.ERROR_STATUS, self.emsg

        return self.SUCCESS_STATUS

    def get_stock_data(self, path="", code="", start="", end="", header_num=1):
        """
        description : 銘柄コードから株価データのデータフレームを取得する
        args        : code -> データを取得する対象コード
                    : path -> csv保管ディレクトリ
                    : start -> データを取得する期間の開始日
                    : end -> データを取得する期間の終了日
                    : header_num -> 読み取るヘッダーの開始点(デフォルト 1)
        return      : stock_data -> 取得したデータ(DataFrame)
        @後でcodeを使ってデータを取得するように修正する
        """
        if not path == "":
            cwd = os.getcwd()
            os.chdir(path)

        # 株価データの存在確認
        if type(self.check_path(0)) != bool:
            self.emsg = self.check_path(0)[self.POS_MSG]
            return self.ERROR_STATUS, self.emsg

        try:
            # 株価データの取得
            stock_data = pd.read_csv(
                self.StockPath,
                header=header_num,
                encoding='ms932',
                names=['date',
                       'opening',
                       'high',
                       'low',
                       'closing',
                       'volume',
                       'adjustment']
            )
        except Exception:
            self.emsg = '[:ERROR:] {} で例外が発生しました。'.format(sys._getframe().f_code.co_name)
            return self.ERROR_STATUS, self.emsg, traceback.print_exc()

        if not path == "":
            os.chdir(cwd)

        if start != "":
            if dc.DateCheck(start):
                start = dc.DateUTime(start)
            else:
                self.emsg = '[:ERROR:] {} でエラーが発生しました。'.format(sys._getframe().f_code.co_name)
                return self.ERROR_STATUS, self.emsg
            # start以降の日付のデータ取得
            stock_from_start = stock_data[stock_data['date'] >= start]
        else:
            stock_from_start = stock_data

        if end != "":
            if dc.DateCheck(end):
                # start と endをUnix形式にする
                end = dc.DateUTime(end)
            else:
                self.emsg = '[:ERROR:] {} でエラーが発生しました。'.format(sys._getframe().f_code.co_name)
                return self.ERROR_STATUS, self.emsg
            # end以前の日付のデータ取得
            stock_from_start_by_end = stock_data[end >= stock_from_start['date']]
        else:
            stock_from_start_by_end = stock_from_start

        # indexを初期化した状態でstock_dataに格納
        stock_data = stock_from_start_by_end.reset_index(drop=True)
        return stock_data

    def get_senti_data(self, path="", code="", start="", end=""):
        """
        description : 銘柄コードからセンチメントデータのデータフレームを取得する
        args        : code -> データを取得する対象コード
                    : start -> データを取得する期間の開始日
                    : end -> データを取得する期間の終了日
        return      : senti_data -> 取得したデータ(DataFrame)
        @後でcodeを使ってデータを取得するように修正する
        """
        if not path == "":
            cwd = os.getcwd()
            os.chdir(path)

        # センチメントデータ、株価データの存在確認
        if type(self.check_path(mode=1)) != bool:
            self.emsg = self.check_path(mode=1)[self.POS_MSG]
            return self.ERROR_STATUS, self.emsg

        try:
            # センチメントデータの取得
            senti_data = pd.read_csv(
                self.SentiPath,
                header=0,
                names=['company name',
                       'date',
                       'positive',
                       'neutral',
                       'negative']
            )
        except Exception:
            self.emsg = '[:ERROR:] {} で例外が発生しました。'.format(sys._getframe().f_code.co_name)
            return self.ERROR_STATUS, self.emsg

        if not path == "":
            os.chdir(cwd)

        if start != "":
            if dc.DateCheck(start):
                # start以降の日付のデータ取得
                senti_from_start = senti_data[senti_data['date'] >= start]
            else:
                self.emsg = '[:ERROR:] {} でエラーが発生しました。'.format(sys._getframe().f_code.co_name)
                return self.ERROR_STATUS, self.emsg
        else:
            senti_from_start = senti_data

        if end != "":
            if dc.DateCheck(start) and dc.DateCheck(end):
                # start と endをUnix形式にする
                end = dc.DateUTime(end)
            else:
                self.emsg = '[:ERROR:] {} でエラーが発生しました。'.format(sys._getframe().f_code.co_name)
                return self.ERROR_STATUS, self.emsg

            # end以前の日付のデータ取得
            senti_from_start_by_end = senti_data[end >= senti_from_start['date']]
        else:
            senti_from_start_by_end = senti_from_start

        # indexを初期化した状態でstock_dataに格納
        senti_data = senti_from_start_by_end.reset_index(drop=True)
        return senti_data

    def get_stock_and_senti(self, code, start="", end=""):
        """
        description: 銘柄コードからセンチメントデータと株価データからデータフレームを取得する
        arg:
            start:取得開始日(YYYYMMDD 文字列)
            end:取得終了日(YYYYMMDD 文字列)
        """
        # 株価データの取得
        stock_data = self.get_stock_data(code, start="", end="")
        # センチメントデータの取得
        senti_data = self.get_senti_data(code, start="", end="")

        return senti_data, stock_data

    def comp_stock_na_csv_file(self, csv_file_path):
        """株価データのcsvファイル内のデータを線形補完する

        Args:
            csv_file_path (str): 対象株価データcsvファイル
        Return:
            False or 株価データ(DataFrame)
        """
        rtn = False

        if not os.path.exists(csv_file_path):
            return rtn

        self.StockPath = csv_file_path
        # csvファイルから株価情報をDataFrameで取得
        stock_data = self.get_stock_data()
        # 株価データの欠損日日付リストを取得
        na_list = self.find_stock_na_date(stock_data)
        # 株価データを線形補完する
        stock_data = self.comp_stock_na(stock_data, na_list, round_digit=1)

        return stock_data

# //////////////
# //   TEST   //
# //////////////
if __name__ == '__main__':
    s3 = S3StatsCSV()
