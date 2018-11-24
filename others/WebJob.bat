REM ///////////////////////////////////////////////////////////////////
REM // name        : WebJob.bat
REM // description : Azure WebJobに登録し、株価データとセンチメントデータ
REM //             : 更新をキックする
REM // date        : 2018/11/24
REM ///////////////////////////////////////////////////////////////////

cd /d %~dp0
REM 処理実行(パスは環境変数から取得する設計)
python %DL_STOCK_DATA_MOD%
python %DL_SENTIMENT_DATA_MOD%
