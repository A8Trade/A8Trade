import pandas as pd
from pandas import DataFrame


def calculateMacdHightCount(params: DataFrame):
    if (params['MAD_Column'].iloc[len(df) - 1] < 0):
        if df['macd_hight_count'].iloc[len(df) - 2] < 0:
            df['macd_hight_count'].iloc[len(df) - 1] = df['macd_hight_count'].iloc[len(df) - 2] - 1
        else:
            df['macd_hight_count'].iloc[len(df) - 1] = -1

    else:
        if df['macd_hight_count'].iloc[len(df) - 2] > 0:
            df['macd_hight_count'].iloc[len(df) - 1] = df['macd_hight_count'].iloc[len(df) - 2] + 1
        else:
            df['macd_hight_count'].iloc[len(df) - 1] = 1


def is_standard_three(pre_index: int, trend: int, params: DataFrame):
    # todo dp, direction > 0 取正， 小于0 取负
    # todo dp, trend > 0 看空趋势， trend < 0 看多趋势
    start = len(params) - 1
    end = len(params) - 1
    result_standard_three = True
    item = 3
    while start > 0 and item > 0:
        end = start
        start = start - int(abs(params['macd_hight_count'].iloc[start]))
        # 看空趋势
        if trend == 1:
            if item == 3:
                if not (end - start >= 3 and params['macd_hight_count'].iloc[end] > 0):
                    result_standard_three = False
                    break
            elif item == 2:
                if not (end - start >= 5 and params['macd_hight_count'].iloc[end] < 0):
                    result_standard_three = False
                    break
            elif item == 1:
                if not (end - start >= 3 and params['macd_hight_count'].iloc[end] > 0 and end > pre_index > start):
                    result_standard_three = False
                    break
        # 看多趋势
        elif trend == -1:
            if item == 3:
                if not (end - start >= 3 and params['macd_hight_count'].iloc[end] < 0):
                    result_standard_three = False
                    break
            elif item == 2:
                if not (end - start >= 5 and params['macd_hight_count'].iloc[end] > 0):
                    result_standard_three = False
                    break
            elif item == 1:
                if not (end - start >= 3 and params['macd_hight_count'].iloc[end] < 0 and end > pre_index > start):
                    result_standard_three = False
                    break
        item = item - 1
    return result_standard_three


def calculateGroup(data: tuple, params: DataFrame):
    # todo dp, direction > 0 取正， 小于0 取负
    result = {}
    for item in data:
        res = item
        end = len(params) - 1
        start = len(params) - 1
        print(f"查第{item}个hight")
        while item > 0:
            end = start
            start = start - int(abs(params['macd_hight_count'].iloc[start]))
            item = item - 1
        group_info = {}
        if params['macd_hight_count'].iloc[start] < 0:
            group_info["direction"] = -1
        elif params['macd_hight_count'].iloc[start] > 0:
            group_info["direction"] = 1
        else:
            group_info["direction"] = 0
        group_info["between"] = [start, end]
        result[res] = group_info
    return result


def calculateGroup2(data: tuple, params: DataFrame):
    result = {}
    for item in data:
        end = start = len(params) - 1
        print(f"查第{item}个hight")
        while start > 0 and item > 0:
            end = start
            start = start - abs(params['macd_hight_count'].iloc[start])
            item = item - 1
        result[item] = [start, end]
    return result


# 创建示例 DataFrame
data = {
    'Date': pd.date_range(start='2022-01-01', periods=40),
    'Close': [
        100, 110, 120, 130, 125, 120, 110, 100, 90, 80,
        81, 82, 83, 84, 85, 86, 87, 88, 89, 90,
        101, 102, 103, 104, 105, 106, 107, 108, 99, 100,
        100, 110, 120, 130, 125, 120, 110, 100, 90, 80,

    ]
}

df = pd.DataFrame(data)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
df['macd_hight_count'] = 0
print(df)
df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 81}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
print(df)
print(len(df))
print("=========")
print(df['Close'].iloc[len(df) - 1])

calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 82}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 100}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 101}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 102}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 103}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 100}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 90}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)


df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 120}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 121}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 130}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 140}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 145}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)


df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 135}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 132}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)

df = df.append({'Date': '2022-02-10 00:00:00', 'Close': 130}, ignore_index=True)
df['MA'] = df['Close'].rolling(window=3).mean()
df['Deviation'] = df['Close'] - df['MA']
df['MAD_Column'] = df['Deviation'] - df['Deviation'].abs().mean()
calculateMacdHightCount(df)
print(df)
print(is_standard_three(45, -1, df))