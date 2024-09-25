# -*- coding: utf-8 -*-
"""data_preprocessing.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NCRMAPhxbAOa4svITIcmNIozJYlH3oQ1
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

"""Đọc dữ liệu từ file "inf.csv" và lưu kết quả vào DataFrame df_info."""

df_info = pd.read_csv('./Tiền xử lý dữ liệu/inf.csv')
df_info = df_info.set_index('Id').sort_index()
df_info

"""Kiểm tra xem trong tập có dòng nào bị trùng không. Nếu trùng thì trả về True, không thì là False"""

num_duplicated_rows = df_info.duplicated().sum()
is_duplicated = (num_duplicated_rows != 0)
print('So dong lap la {}'.format(num_duplicated_rows))
print(is_duplicated)

"""Xóa các dòng trùng lặp, giữ lại dòng gần nhất"""

df_info = df_info.drop_duplicates()
num_duplicated_rows = df_info.duplicated().sum()
print('So dong lap la {}'.format(num_duplicated_rows))

"""Kiểm tra dạng dữ liệu của các cột để xem có đúng với dạng mong muốn không."""

df_info.dtypes

"""- Square: loại bỏ đơn vị m^2 và chuyển sang dạng số"""

df_info["Square"] =df_info["Square"].str.replace('m²','')
df_info["Square"] = pd.to_numeric(df_info["Square"],errors='coerce')
df_info.rename(columns={'Square':'Square(m²)'},inplace=True)
df_info['Square(m²)']

"""
- Price: Xem cụ thể hơn các giá trị để có thể xử lý chính xác

"""

df_info["Price"].unique()

"""Thấy có các dạng đơn vị là Triệu/tháng, Nghìn/tháng, Triệu/m2/tháng, Nghìn/m2/tháng, và có thêm một kiểu giá trị là Thỏa thuận.
Cần chuyển toàn bộ đơn vị sang Triệu/tháng và loại bỏ đơn vị ở sau để tiện chuyển thành số, riêng giá trị Thỏa thuận thì để là NaN
"""

def convert_price(price,square):
    if 'Triệu/tháng' in price:
        price = price.replace('Triệu/tháng','')
        return float(price)
    if 'Trăm nghìn/tháng' in price:
        price = price.replace('Nghìn/tháng','')
        return float(price)/1000
    if 'Triệu/m2/tháng' in price:
        if pd.isna(square):
            return np.nan
        price = price.replace('Triệu/m2/tháng','')
        return float(price)*square
    if 'Nghìn/m2/tháng' in price:
        if pd.isna(square):
            return np.nan
        price = price.replace('Nghìn/m2/tháng','')
        price = float(price)/1000
        return price*square
    return np.nan

df_price_square = df_info[['Price','Square(m²)']]

# Thực hiện chuyển đổi
for i in df_price_square.index:
    df_price_square.at[i,'Price'] = convert_price(df_price_square.loc[i]['Price'],df_price_square.loc[i]['Square(m²)'])

# Lưu vào dataframe
df_info['Price'] =  pd.to_numeric(df_price_square['Price'])
df_info.rename(columns={'Price':'Price(Triệu/tháng)'},inplace=True)

df_info["Price(Triệu/tháng)"]

"""Date: Biểu diễn ngày tháng năm nhưng lại không có dạng dữ liệu là datetime mà là object"""

df_info["Date"] = pd.to_datetime(df_info["Date"],format = "%d/%m/%Y",errors = 'raise')

df_info["Date"]

"""Xử lý dữ liệu NaN:

Vì đây là những thuộc tính khá khó để suy hay đoán và có rất ít dữ liệu nên khi drop nó đi cũng không ảnh hưởng khi xây dựng model sau này.
"""

df_info.isnull().sum()

df_info.dropna(inplace=True)

"""Ouliers

Biểu đồ boxplot để tìm outliers của giá và diện tích
"""

for col in ['Price(Triệu/tháng)','Square(m²)']:
    plt.figure(figsize=(10, 10))
    sns.boxenplot(y=col,data=df_info)
    plt.title('Outliers in {}'.format(col))
    plt.show()

"""Giá có outliers có giá trị trên 100, ta sẽ in những dòng này xem thử"""

outliers_price = df_info[df_info['Price(Triệu/tháng)'] > 100]
outliers_price

"""Thấy giá có outliers có giá trị trên 100 có thể là do người đăng tải thông tin đã nhầm đơn vị nên ta sẽ tiền hành giảm về con số đúng.
Giá đúng của những con số này là khoảng dưới 10.
"""

for i in range(len(outliers_price['Price(Triệu/tháng)'])):
    while(outliers_price['Price(Triệu/tháng)'].iloc[i] >= 10):
        outliers_price['Price(Triệu/tháng)'].iloc[i] /= 10

outliers_price

"""Cập nhập vào df chính"""

df_info.loc[outliers_price.index,'Price(Triệu/tháng)'] = outliers_price['Price(Triệu/tháng)']

"""Còn những điểm trên 50, tiếp tục in ra để xử lý"""

outliers_price = df_info[df_info['Price(Triệu/tháng)'] > 50]
outliers_price

"""Thấy dòng đầu tiên là bán, dòng tiếp là cho thuê cả căn hộ, còn dòng cuối người đăng cũng đã nhập sai giá trị thực nên ta chủ động loại bỏ hết những dòng này."""

df_info.drop(index = outliers_price.index,inplace=True)

"""Thấy giá có outliers có giá trị trên 150 sẽ rơi vào những trường hợp như kí túc xá, hay cho thuê 1 phòng đơn nhưng đăng diện tích cả nhà hoặc đăng sai giá trị thực nên ta cũng loại hết những dòng này."""

outliers_square = df_info[df_info['Square(m²)'] > 150]


df_info.drop(index = outliers_square.index,inplace=True)

"""Biểu đồ boxplot để tìm outliers của giá và diện tích sau khi đã xử lý"""

for col in ['Price(Triệu/tháng)','Square(m²)']:
    plt.figure(figsize=(10, 10))
    sns.boxenplot(y=col,data=df_info)
    plt.title('Outliers in {}'.format(col))
    plt.show()

"""Sắp xếp theo ngày cập nhật gần nhất và lưu df lại vào file clean_data"""

df_info = df_info.sort_values(by='Date', ascending=False)
df_info.to_csv('clean_data.csv')