# 创建一个示例 DataFrame，包含日期和价格
import pandas as pd

import pandas as pd

# 创建一个示例 DataFrame，包含日期和价格
data = {
    'Date': pd.date_range(start='2022-01-01', periods=20),
    'Close': [1, 2, 3, 1, 5, 6, 7, 8, 9, 11, 12, 13, 14, 9, 8, 7, 5, -3, -4, -5]
}

df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# 判断一列的倒数后三个数据是否逐个递增且都大于 0
# last_three_condition = all(df['Values'].tail(3).diff().gt(0)) and all(df['Values'].tail().gt(0))
last_three_condition = all(df['Close'].iloc[-3:].diff().dropna().gt(0)) and all(df['Close'].iloc[-3:] > 0)
#
# print(all(df['Close'].iloc[-3:] > 0))
# print(df['Close'].iloc[-4:].diff().dropna().gt(0))
# print(last_three_condition)




last_three_condition = all(df['Close'].iloc[-3:].diff().dropna().lt(0)) and all(df['Close'].iloc[-3:] < 0)


# print(all(df['Close'].iloc[-3:] > 0))
# print(df['Close'].iloc[-4:].diff().dropna().gt(0))
print(last_three_condition)


