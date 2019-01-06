# ////////////////////////////////////////
# // name: S3DateCulc.py
# // description: 日付計算用
# ////////////////////////////////////////
import datetime
from dateutil.relativedelta import relativedelta

NUM_DAY = 3             # 受け取る引数の数
NUM_DAY_LEN = 8         # 引数の文字列
NUM_DAY_LEN_UNIX = 10   # Unix日付(YYYY-MM-DD)の文字数
NUM_DAY_LEN_SLASH = 10  # 日付(YYYY/MM/DD)の文字数


def DateCheck(Date):
    """
    description : 1.日付(YYYYMMDD 文字列)を受け取り、日付かをチェック
                : 2.日付(YYYY-MM-DD 文字列)を受け取り、日付かをチェック
                : 3.日付(YYYY/MM/DD 文字列)を受け取り、日付かをチェック
    args        : Date -> 文字列
    return      : True/False
    """
    # パターン1
    if len(Date) == NUM_DAY_LEN:
        try:
            datetime.datetime.strptime(Date, '%Y%m%d')
            return True
        except ValueError:
            return False
    # パターン2
    if len(Date) == NUM_DAY_LEN_UNIX:
        try:
            datetime.datetime.strptime(Date, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    # パターン3
    if len(Date) == NUM_DAY_LEN_SLASH:
        try:
            datetime.datetime.strptime(Date, '%Y/%m/%d')
            return True
        except ValueError:
            return False

    return False


def today():
    """当日日付を文字列で返す(YYYY-MM-DD)"""
    today = datetime.datetime.today()
    rtn = datetime.datetime.strftime(today, "%Y-%m-%d")

    return rtn


def month_delta(start_day, month="", week=""):
    """開始日からnヶ月後(前) or n週間後(前)の日を計算して返す

    Args:
        start_day (datetime): 開始日
        month (int): nヶ月後(前)
    """
    if type(start_day) == str:
        start_day = datetime.datetime.strptime(start_day, "%Y-%m-%d")

    if month and week:
        return False

    if month:
        target_day = start_day + relativedelta(months=month)

    if week:
        target_day = start_day + relativedelta(weeks=week)

    return target_day


def DateConv(day, mode=0):
    """
    description: datetime型日付を受け取り、文字列にして返却する
    args       : mode
               :  0 -> 日付をYYYYMMDDで返す
               :  1 -> 日付をYYYY-MM-DDで返す
               :  2 -> 日付をYYYY/MM/DDで返す
    """
    if mode == 0:
        return day.strftime('%Y%m%d')
    if mode == 1:
        return day.strftime('%Y-%m-%d')
    if mode == 2:
        return day.strftime('%Y/%m/%d')
    else:
        return False


def CharConv(day, mode=0):
    """
    description : 日付の文字列を日付型や別の文字列にして返す
    args        : day -> 文字型の日付
                : mode
                :   0 -> (default) 文字列を日付型にして返す
                :   1 -> 日付の文字列について、YYYYMMDDはYYYY-MM-DDに、
                :        YYYY-MM-DDはYYYYMMDDに変換する
    return      : 日付(datetime型) or False
    """
    rtn = False
    # 日付型の文字列かを確認
    if not DateCheck(day):
        return rtn

    # MODE1:文字列を日付型にして返す場合
    if mode == 0:
        # YYYYMMDDの可能性をチェック
        try:
            rtn = datetime.datetime.strptime(day, '%Y%m%d')
            return rtn
        except ValueError:
            # YYYY-MM-DDの可能性をチェック
            try:
                rtn = datetime.datetime.strptime(day, '%Y-%m-%d')
                return rtn
            except ValueError:
                # YYYY/MM/DDの可能性をチェック
                try:
                    rtn = datetime.datetime.strptime(day, '%Y/%m/%d')
                    return rtn
                except ValueError:
                    return rtn
    # MODE2:文字列を別の形の文字列にして返す場合
    elif mode == 1:
        # YYYYMMDDをYYYY-MM-DD形式にする
        if len(day) == NUM_DAY:
            rtn = day[0:4] + day[4:6] + day[6:8]
            return rtn

        # YYYY-MM-DDをYYYYYMMDD形式にする
        if len(day) == NUM_DAY_LEN_UNIX:
            rtn = day[0:4] + day[5:7] + day[8:10]
            return rtn

    return rtn


def DateDiff(StartDay, EndDay):
    """
    description : 開始日と終了日を受け取り、日付の差分を返す
    args        : StartDay -> 文字列
                : EndDay   -> 文字列
                :     YYYYMMDD   形式
                :     YYYY-MM-DD 形式
                :     YYYY/MM/DD 形式
    return      : datetime型日付 or False
    """
    rtn = False
    # args check
    if DateCheck(StartDay) and DateCheck(EndDay):
        if len(StartDay) == NUM_DAY_LEN and len(EndDay) == NUM_DAY_LEN:
            Start = datetime.datetime.strptime(StartDay, '%Y%m%d')
            End = datetime.datetime.strptime(EndDay, '%Y%m%d')
            rtn = (End - Start).days
            return rtn

        if len(StartDay) == NUM_DAY_LEN_UNIX and len(EndDay) == NUM_DAY_LEN_UNIX:
            # StartDayとEndDayが'-'を含むかチェック
            if StartDay.count('-') > 0 and EndDay.count('-') > 0:
                Start = datetime.datetime.strptime(StartDay, '%Y-%m-%d')
                End = datetime.datetime.strptime(EndDay, '%Y-%m-%d')
                rtn = (End - Start).days
                return rtn

        if len(StartDay) == NUM_DAY_LEN_SLASH and len(EndDay) == NUM_DAY_LEN_SLASH:
            # StartDayとEndDayが'/'を含むかチェック
            if StartDay.count('/') > 0 and EndDay.count('/') > 0:
                Start = datetime.datetime.strptime(StartDay, '%Y/%m/%d')
                End = datetime.datetime.strptime(EndDay, '%Y/%m/%d')
                rtn = (End - Start).days
                return rtn

    return rtn


def DateAdd(StartDay, AddDay):
    """
    description : 日付と何日加えるかを引数として受け取り、結果を返す
    args        : StartDay -> 開始日 (YYYYMMDD形式の文字列)
                : AddDay -> 加算する日数 (数値)
    return      : 加算した後の日付 (datetime型)
    """
    if len(StartDay) != NUM_DAY_LEN:
        print('[:ERROR:] Your input:={0} but must be YYYYYMMDD format'.format(StartDay))

    # get datetime from StartDay(str)
    Start = datetime.datetime.strptime(StartDay, '%Y%m%d')
    result = Start + datetime.timedelta(days=AddDay)
    return result


def DateUTime(Date):
    """
    description: １．日付(YYYYMMDD 文字列)を受け取り、Unix用の形式(YYYY-MM-DD)に変換する    
                 ２．日付(YYYY-MM-DD 文字列)を受け取り、日付型に変換する
    """
    if not (DateCheck(Date) and DateCheck(Date)):
        print('[:ERROR:] Wrong input')
        return False
    # パターン１
    if len(Date) == NUM_DAY_LEN and DateCheck(Date):
        return Date[0:4] + '-' + Date[4:6] + '-' + Date[6:8]
    # パターン２
    if len(Date) == NUM_DAY_LEN_UNIX and DateCheck(Date):
        return datetime.datetime.strptime(Date, '%Y-%m-%d')


def DateList(start, end):
    """
    description:日付のlistを生成する(startとendを含む).
    args:
       start -> datetime型日付
       end   -> datetime型日付
    """
    day_list = []
    diff = DateDiff(DateConv(start), DateConv(end))
    # startとendの差分回数回す
    i = 0
    while i < diff + 1:
        if i == 0:  # 初回は加算しないでlistに追加する
            date = DateConv(start, 1)
            day_list.append(date)
        else:  # 初回以外は1日加算してlistに追加する
            start = DateAdd(DateConv(start), 1)
            # YYYY-MM-DD形式の文字列に変換
            date = DateConv(start, 1)
            day_list.append(date)
        i += 1

    return day_list

# for test
if __name__ == "__main__":
    a = DateDiff('20181110', '20181120')
    print('DateDiff:{0}'.format(a))
    b = DateAdd('20181110', 1)
    print('DateAdd:{0}'.format(b))
    c = DateUTime('20181110')
    print('DateUTime:{0}'.format(c))
    d1 = '20181110'  # normal
    d2 = '2018-11-10'  # error
    print('20181110 is:{0}, 2018-11-10 is:{1}'.format(DateCheck(d1), DateCheck(d2)))
    print('---DayList---')
    start = datetime.datetime.strptime('20181010', '%Y%m%d')
    end = datetime.datetime.strptime('20181020', '%Y%m%d')
    day_list = DateList(start, end)
    print(day_list)
    print('---DayList---')
    e = CharConv('2018-10-10', mode=1)
    print(e)
