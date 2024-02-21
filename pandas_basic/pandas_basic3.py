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

# 计算能量柱子的起始和终止
def identify_energy_bar_ranges(histogram):
    start_index = None
    ranges = []

    for i in range(len(histogram)):
        if histogram[i] > 0 and start_index is None:
            start_index = i
        elif histogram[i] <= 0 and start_index is not None:
            ranges.append((start_index, i - 1))
            start_index = None

    # 处理最后一个能量柱子的情况
    if start_index is not None:
        ranges.append((start_index, len(histogram) - 1))

    return ranges

# 输出结果
energy_bar_ranges = identify_energy_bar_ranges(df['MACD_Histogram'])
print("Energy Bar Ranges:", energy_bar_ranges)
