import pandas as pd

data = pd.Series([3, 4, 5, 6, 7])
print('1.使用列表创建:', data)

data = pd.Series([3, 4, 5, 6, 7], index=['a', 'b', 'c', 'd', 'e'])

print(data)

print("=========3.使用list列表制定index===========")
data = pd.Series([3, 4, 5, 6, 7], index=list("abcde"))
print(data)

print("=========4.使用字典初始化数据===========")
population_dict = {'ch': 2800, 'bj': 3000, 'gz': 1500, 'sz': 1200}
population_series = pd.Series(population_dict)
print(population_series)

print("=========5.使用字典初始化数据，且指定key===========")
population_dict = {'ch': 2800, 'bj': 3000, 'gz': 1500, 'sz': 1200}
population_series = pd.Series(population_dict, index=['ch', 'bj'])
print(population_series)


print("6.查看Series的索引index:", data.index)
print("7.查看Series的索引values:", data.values)