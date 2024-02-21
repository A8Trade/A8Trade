import pandas as pd  # 别名

# print(pd.__version__)

pd.set_option('expand_frame_repr', False)  # 当列太多时不换行
pd.set_option('display.max_rows', 1000)  # 最多显示行数.
# pd.set_option('precision', 6)  # 浮点数的精度】
pd.set_option('display.float_format', lambda x: '%.2f' % x)  # 设置不用科学计数法，保留两位小数.

# 更多设置可以参考文档：http://pandas.pydata.org/pandas-docs/stable/user_guide/options.html

# =====导入数据
import os

print(os.path.dirname(__file__))
print(os.path.dirname(os.path.dirname(__file__)))

# comma separate value ,
df = pd.read_csv(filepath_or_buffer='../data/BNBUSDT_vnpy.csv')
# pd.read_excel()
# pd.read_hdf()

new_row = {
    "Datetime":"2024-08-01 00:00:00",
    "open_time": "1627747200000",
    'Open': "1627747200000",
    'High': "329.63",
    'Low': "330.00",
    'Close': "329.54",
    'Volume': "1406.58"
}
df.append(new_row, ignore_index=True)
print(df[0])
