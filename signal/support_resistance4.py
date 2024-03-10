import pandas as pd

# Create a sample DataFrame
data = {'close': [10, 15, 5, 20, 8]}
df = pd.DataFrame(data)

# Calculate the rolling minimum using a window size of 2
df['rolling_min'] = df['close'].rolling(window=2).min()

# Filter out rows where the current close value is equal to the rolling minimum
new_df = df[df['close'] == df['rolling_min']]
print(new_df)


import pandas as pd

# 创建一个示例 DataFrame
data = {'column1': [1, 2, 3, 4, 5],
        'column2': ['A', 'B', 'C', 'D', 'E']}
df = pd.DataFrame(data)

# 定义处理函数，这里示例是将两列数据转换为字符串再拼接
def process_row(row):
    return str(row['column1']) + '_' +row['column2']

# 对两列数据进行处理后拼接成一个列表
processed_list = df.apply(process_row, axis=1).tolist()

print(processed_list)


import pandas as pd

# 创建示例 DataFrame
df = pd.DataFrame({'A': [1, 2, 3],
                   'B': ['a', 'b', 'c'],
                   'C': [10.5, 20.3, 15.8]})

# 选择要转换为字典的行（例如第一行，索引为0）
row_index = 0
row_dict = df.iloc[row_index].to_dict()

# 打印结果
print(row_dict)
