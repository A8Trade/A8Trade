import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# 创建示例 DataFrame
data = {
    'Date': pd.date_range(start='2022-01-01', periods=50),
    'Close': [100, 110, 120, 125, 130, 120, 110, 100, 90, 80,
              85, 75, 70, 65, 60, 65, 70, 75, 80, 85,
              90, 85, 80, 75, 70, 65, 70, 75, 80, 85,
              90, 100, 110, 120, 125, 130, 120, 110, 100, 90,
              80, 85, 75, 70, 65, 60, 65, 70, 75, 80]
}

df = pd.DataFrame(data)

# 识别头肩顶形态
def identify_head_and_shoulders(df):
    # 找到峰值
    peaks, _ = find_peaks(df['Close'])

    if len(peaks) < 3:
        return False  # 没有足够的峰值

    # 从峰值中找到可能的头肩顶形态
    for i in range(1, len(peaks) - 1):
        peak_left = df['Close'][peaks[i - 1]]
        peak_center = df['Close'][peaks[i]]
        peak_right = df['Close'][peaks[i + 1]]

        if peak_center > peak_left and peak_center > peak_right:
            return True, peaks[i]  # 发现头肩顶形态及其位置

    return False, None  # 没有发现头肩顶形态

# 画出股价曲线
plt.plot(df['Date'], df['Close'], label='Stock Price')

# 找到可能的头肩顶形态
peaks, _ = find_peaks(df['Close'])
# 标记峰值
plt.plot(df['Date'][peaks], df['Close'][peaks], 'x', label='Peaks')

# 输出结果
found, head_and_shoulders_index = identify_head_and_shoulders(df)
if found:
    print("可能存在头肩顶形态")
    # 标记头肩顶形态的位置
    plt.annotate('Head and Shoulders', xy=(df['Date'][head_and_shoulders_index], df['Close'][head_and_shoulders_index]),
                 xytext=(df['Date'][head_and_shoulders_index] + pd.DateOffset(days=5), df['Close'][head_and_shoulders_index] + 5),
                 arrowprops=dict(facecolor='red', arrowstyle='wedge,tail_width=0.7', alpha=0.7))

plt.title('Stock Price with Possible Head and Shoulders Pattern')
plt.legend()
plt.show()