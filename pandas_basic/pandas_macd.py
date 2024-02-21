import pandas as pd
import numpy as np

# 创建示例 DataFrame
data = {
    'Date': pd.date_range(start='2022-01-01', periods=100),
    'Close': np.random.randint(90, 110, 100)
}

df = pd.DataFrame(data)

# 计算移动平均线
window = 10  # 可根据实际情况调整
df['MA'] = df['Close'].rolling(window=window).mean()

# 计算价格与移动平均线的偏离
df['Deviation'] = df['Close'] - df['MA']

# 计算MAD
mad = df['Deviation'].abs().mean()

# 计算MAD柱子
df['MAD_Column'] = df['Deviation'] - mad

# 找到MAD柱子的负值和正值的起始位置
negative_start = df[df['MAD_Column'] < 0].index[0]
positive_start = df[df['MAD_Column'] > 0].index[0]

print("MAD柱子负值起始位置:", negative_start)
print("MAD柱子正值起始位置:", positive_start)
print(df)