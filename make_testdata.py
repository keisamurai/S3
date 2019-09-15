import random, string
import pandas as pd
import datetime
import matplotlib.pyplot as plt


def DateAdd(StartDay, AddDay):
    """
    description : 日付と何日加えるかを引数として受け取り、結果を返す
    args        : StartDay -> 開始日 (YYYY-MM-DD形式の文字列)
                : AddDay -> 加算する日数 (数値)
    return      : 加算した後の日付 (datetime型)
    """
    # get datetime from StartDay(str)
    Start = datetime.datetime.strptime(StartDay, '%Y-%m-%d')
    result = Start + datetime.timedelta(days=AddDay)
    return result


def randomname(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)


def make_user_test_data(n):
    """
    description:ユーザーデータをテスト用にn行生成する
    input      :n -> (int) 生成するテストデータの行数
    output     :'users.csv'という名前でテストデータを作成
    """
    for i in range(n):
        user_id = randomname(6)
        df = pd.DataFrame([[user_id.upper(), '20_early', random.randint(1,2)]],
            columns=['id', 'age', 'gender'])
        df.to_csv('users.csv', sep=',', mode='a', header=False, index=False)
    
    df = pd.read_csv('users.csv', header=None)
    return 


def make_fitbit_test_data():
    """
    description:テスト用の１か月分のfitbitデータを生成する。
                生成については、元データの平均と標準偏差からランダムに生成
                <必要データ>
                    ID, Record_Date, Activity_StepsTotal, Sleep_minutesAsleep, Sleep_efficiency
    """
    # settings
    base_day = '2016-09-01' # 日付開始日
    days = 30               # 期間
    mean_AS = 10116
    mean_MA = 349
    mean_SE = 90.9
    std_AS = 4790
    std_MA = 118
    std_SE = 10

    df = pd.read_csv('users.csv', header=None)
    df.columns = ['id', 'age', 'gender']

    # データ生成
    for user_id in df['id']:
        for day in range(days):
            next_day = DateAdd(base_day, day)
            Record_Date = next_day.strftime('%Y-%m-%d')

            Activity_StepsTotal = mean_AS + random.randint(-std_AS, std_AS)
            Sleep_minutesAsleep = mean_MA + random.randint(-std_MA, std_MA)
            Sleep_efficiency = mean_SE + random.randint(-std_SE, std_SE)

            df_fitbit_test = pd.DataFrame([[user_id, Record_Date, Activity_StepsTotal, Sleep_minutesAsleep, Sleep_efficiency]],
                         columns=['id', 'Record_Date', 'Activity_StepsTotal', 'Sleep_minutesAsleep', 'Sleep_efficiency'])

            df_fitbit_test.to_csv('fitbit_test.csv', sep=',', mode='a', header=False, index=False)

    return


def calc_score(AS, MA, SE):
    score = AS * MA * SE
    return score
 

def show_machart(df, ma1=7, ma2=14, start=False, end=False):
    t_items = ['Activity_StepsTotal', 'Sleep_minutesAsleep', 'Sleep_efficiency']

    df_users = pd.read_csv('users.csv', header=None)
    df_users.columns = ['id', 'age', 'gender']

    for user_id in df_users['id']:
        for t_item in t_items:
            df_target = df[df['id'] == user_id]
            ma_1 = pd.Series.rolling(df_target[t_item], window=ma1).mean()
            ma_2 = pd.Series.rolling(df_target[t_item], window=ma2).mean()
    
            xdate = [x for x in df_target.index]
    
            plt.figure(figsize=(15,5))
            plt.style.use('ggplot')
    
            close = df_target[t_item]
    
            if start:
                xmin = start
            else:
                xmin = df_target.index[0]
            if end:
                xmax = end
            else:
                xmax = df_target.index[-1]
    
            ymin = close.loc[xmin:xmax].min() - 50
            ymax = close.loc[xmin:xmax].max() + 50
    
            label = '{0}_{1}'.format(user_id, t_item)

            plt.plot(xdate, close ,color="b",lw=1,linestyle="dotted",label=label)
            plt.plot(xdate, ma_1, label="Moving Average {} days".format(ma1))
            plt.plot(xdate, ma_2, label="Moving Average {} days".format(ma2))
            plt.legend(loc='best')
            plt.ylim(ymin, ymax)
            plt.xlim(xmin, xmax)
            plt.show()
    
    return


def make_madata(df, ma1=7, ma2=14, start=False, end=False):
    t_items = ['Activity_StepsTotal', 'Sleep_minutesAsleep', 'Sleep_efficiency']

    df_users = pd.read_csv('users.csv', header=None)
    df_users.columns = ['id', 'age', 'gender']

    df_rtn = df
    count_u = 0
    for user_id in df_users['id']:
        count_i = 0
        for t_item in t_items:
            df_target = df[df['id'] == user_id]
            ma_1 = pd.Series.rolling(df_target[t_item], window=ma1).mean()
            ma_2 = pd.Series.rolling(df_target[t_item], window=ma2).mean()

            ma_1.name = 'ma_1_{}'.format(t_item)
            ma_2.name = 'ma_2_{}'.format(t_item)

            if count_i == 0:
                temp = pd.concat([df_target[df['id'] == user_id], ma_1, ma_2], axis=1)
                df_temp = temp
            else:
                df_temp = pd.concat([df_temp, ma_1, ma_2], axis=1)

            count_i = count_i + 1

        # df_rtnの生成
        if count_u == 0:
            df_rtn = df_temp
        else:
            df_rtn = pd.concat([df_rtn, df_temp], axis=0)
        

        # df_temp 初期化
        df_temp = None
        count_u = count_u + 1

    return df_rtn


if __name__ == '__main__':
    # make_user_test_data(5)
    # make_fitbit_test_data()
    df = pd.read_csv('fitbit_test.csv', header=None)
    df.columns = ['id', 'Record_Date', 'Activity_StepsTotal', 'Sleep_minutesAsleep', 'Sleep_efficiency']
    show_machart(df)
    df = make_madata(df)
    print(df)
