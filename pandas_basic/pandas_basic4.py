import pandas as pd

# 示例字典数据存储在变量中
data_dict_variable = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 22],
    'City': ['New York', 'San Francisco', 'Los Angeles']
}

# 创建 DataFrame
df_variable = pd.DataFrame(data_dict_variable)

# 打印 DataFrame
print(df_variable)
