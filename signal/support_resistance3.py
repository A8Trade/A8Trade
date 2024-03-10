import pandas as pd

# 创建一个示例 DataFrame
data = {'Date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
        'Close': [50, 45, 55, 40, 60]}

df = pd.DataFrame(data)

# 指定窗口大小
window_size = 3

# 计算 'Close' 列在指定窗口内的最小值
df["min_value"] = df['Close'].rolling(window=window_size, min_periods=1).min()

# 找到最小值所在的行
new_df = df[df['Close'] == df['min_value']]

# 打印结果
print(new_df)
