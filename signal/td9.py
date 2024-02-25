import pandas as pd

data = {'date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05',
                 '2022-01-06', '2022-01-07', '2022-01-08', '2022-01-09', '2022-01-10'],
        'close': [100, 105, 110, 95, 92, 87, 89, 92, 91, 90]}
df = pd.DataFrame(data)

end = len(df)
print(end)

for i in range(end):
    print(i)
