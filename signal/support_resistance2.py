import pandas as pd

window_size = 20


def process_row(row):
    return f"价格:{str(row['Close'])}, 时间:{row['Datetime']}"


def group_close_values(dataframe, threshold=0.005):
    grouped_values = []
    current_dataframe = dataframe.iloc[[0]]
    for i in range(1, len(dataframe)):
        if abs(dataframe['Close'].iloc[i] - current_dataframe['Close'].iloc[0]) / current_dataframe['Close'].iloc[
            0] <= threshold:
            current_dataframe = current_dataframe.append(dataframe.iloc[i].to_dict(), ignore_index=True)
        else:
            # 当差异超过阈值时，检查当前组的元素数量
            average_value = current_dataframe['Close'].mean()
            grouped_values.append(average_value)
            print(
                f"len: {len(current_dataframe)}, average_value:{average_value},current_group:{current_dataframe.apply(process_row, axis=1).tolist()}")
            current_dataframe = dataframe.iloc[[i]]

    # 处理最后一组
    if len(current_dataframe) > 0:
        average_value = current_dataframe['Close'].mean()
        grouped_values.append(average_value)
        print(
            f"len: {len(current_dataframe)}, average_value:{average_value},current_group:{current_dataframe.apply(process_row, axis=1).tolist()}")

    return grouped_values


def getSupport(dataframe, threshold=0.005):
    dataframe["min_value"] = dataframe['Close'].rolling(window=window_size, min_periods=1).min()
    df_min_value = dataframe[dataframe['Close'] == dataframe['min_value']]
    df_min_value = df_min_value.sort_values(by='Close')
    grouped_min_values_support = group_close_values(df_min_value, threshold)
    print(grouped_min_values_support)
    # 计算 Close 列的滚动窗口最大值
    dataframe["max_value"] = dataframe['Close'].rolling(window=window_size, min_periods=1).max()
    df_max_value = dataframe[dataframe['Close'] == dataframe['max_value']]
    # 找到 Close 列滚动窗口最小值的索引
    df_max_value = df_max_value.sort_values(by='Close')
    # 调用 group_close_values 函数
    grouped_max_values_pressure = group_close_values(df_max_value, threshold)
    print(grouped_max_values_pressure)
    grouped_min_values_support.extend(grouped_max_values_pressure)
    return grouped_min_values_support


# 从某个数据源获取K线数据，这里假设使用CSV文件
df = pd.read_csv('BTCUSDT_vnpy_3min.csv')  # 替换成你的实际数据源
print(getSupport(df, 0.005))
