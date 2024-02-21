import pandas as pd

# 创建一个示例 DataFrame
data = {
    'Date': pd.date_range(start='2022-01-01', periods=10),
    'Close': [100, 105, 110, 95, 98, 105, 112, 120, 115, 110]
}

df = pd.DataFrame(data)

# 计算 MACD 和信号线
short_window = 3
long_window = 6
signal_window = 3

df['Short_MA'] = df['Close'].ewm(span=short_window, adjust=False).mean()
df['Long_MA'] = df['Close'].ewm(span=long_window, adjust=False).mean()

df['MACD'] = df['Short_MA'] - df['Long_MA']
df['Signal_Line'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()

# 计算 MACD 能量柱子
df['MACD_Histogram'] = df['MACD'] - df['Signal_Line']

# 提取正能量和负能量的日期区域
positive_energy_dates = df[df['MACD_Histogram'] > 0]['Date']
negative_energy_dates = df[df['MACD_Histogram'] < 0]['Date']

# 输出结果
print("Positive Energy Dates:")
print(positive_energy_dates)

print("\nNegative Energy Dates:")
print(negative_energy_dates)
