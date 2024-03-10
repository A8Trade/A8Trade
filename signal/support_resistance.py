import pandas as pd
import matplotlib.pyplot as plt
import talib

# 从某个数据源获取K线数据，这里假设使用CSV文件
df = pd.read_csv('DOGEUSDT_vnpy.csv')  # 替换成你的实际数据源

# 标记支撑与阻力位
support_levels = df['Close'].rolling(window=24, min_periods=1).min()
resistance_levels = df['Close'].rolling(window=24, min_periods=1).max()


# 获取支撑或者阻力值
def group_close_values(sorted_list, threshold=0.005):
    grouped_values = []
    current_group = [sorted_list[0]]

    for i in range(1, len(sorted_list)):
        if abs(sorted_list[i] - current_group[-1]) / current_group[-1] <= threshold:
            current_group.append(sorted_list[i])
        else:
            # 当差异超过阈值时，检查当前组的元素数量
            average_value = sum(current_group) / len(current_group)
            grouped_values.append(average_value)
            print(f"len: {len(current_group)}, average_value:{average_value},current_group:{current_group}")
            current_group = [sorted_list[i]]

    # 处理最后一组
    if current_group:
        average_value = sum(current_group) / len(current_group)
        grouped_values.append(average_value)
        print(f"len: {len(current_group)}, average_value:{average_value},current_group:{current_group}")

    return grouped_values


print("支撑值:======")
print(group_close_values(sorted(support_levels)))
print("压力值:======")
print(group_close_values(sorted(resistance_levels)))
