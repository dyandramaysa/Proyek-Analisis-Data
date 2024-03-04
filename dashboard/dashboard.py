import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_result_df(day_df):
    # Membuat dictionary untuk memetakan nilai season
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}

    # Membuat dictionary untuk memetakan nilai yr
    yr_mapping = {0: 2011, 1: 2012}

    # Melakukan operasi grup, mengurutkan, dan memetakan kembali nilai season dan yr
    result = day_df.groupby(["season", "yr"])['cnt'].sum().reset_index().sort_values(by=['yr', 'cnt'], ascending=[True, False])
    result['season'] = result['season'].map(season_mapping)
    result['yr'] = result['yr'].map(yr_mapping)
    
    return result

def create_result2_df(day_df):
    # Membuat dictionary untuk memetakan nilai weathersit
    weather_mapping = {1: 'Clear', 2: 'Mist', 3: 'Light Snow', 4: 'Heavy Rain'}

    # Membuat dictionary untuk memetakan nilai yr
    yr_mapping = {0: 2011, 1: 2012}

    # Menggunakan fungsi agregat untuk menghitung jumlah sepeda yang dirental, nilai minimum, dan maksimum
    result2 = day_df.groupby(["weathersit", "yr"]).agg({'cnt': ['sum', 'min', 'max']}).reset_index()
    result2.columns = ['weathersit', 'year', 'total_rentals', 'min_rentals', 'max_rentals']

    # Memetakan kembali nilai weathersit dan yr
    result2['weathersit'] = result2['weathersit'].map(weather_mapping)
    result2['year'] = result2['year'].map(yr_mapping)

    # Mengurutkan hasil berdasarkan weathersit
    result2 = result2.sort_values(by=['year', 'total_rentals'], ascending=[True, False])
    
    return result2

def create_rentals_by_day_date_df(day_df):
    # Membuat dictionary untuk memetakan nilai yr
    yr_mapping = {0: 2011, 1: 2012}

    # Membuat dataframe untuk informasi jenis hari
    holiday_info = day_df[['dteday', 'yr', 'holiday', 'weekday', 'workingday']]
    holiday_info = holiday_info.drop_duplicates().reset_index(drop=True)

    # Menggunakan lambda function untuk menentukan jenis hari
    holiday_info['day_type'] = holiday_info.apply(lambda row: 'Holiday' if row['holiday'] == 1 else ('Weekend' if row['workingday'] == 0 else 'Workday'), axis=1)

    # Menggabungkan informasi jenis hari dengan data peminjaman sepeda
    merged_df = pd.merge(day_df, holiday_info[['dteday', 'day_type']], on='dteday')

    # Menghitung total peminjaman sepeda untuk setiap jenis hari dan tahun
    rentals_by_day_type = merged_df.groupby(['yr', 'day_type'])['cnt'].sum().reset_index().sort_values(by=['yr', 'cnt'], ascending=[True, False])

    rentals_by_day_type['yr'] = rentals_by_day_type['yr'].map(yr_mapping)

    return rentals_by_day_type

# Load clean data
day_df = pd.read_csv("day_df.csv")

# Filter data
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()
 
with st.sidebar:
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# st.dataframe(main_df)
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

# Menyiapkan berbagai dataframe
result_df = create_result_df(main_df)
result2_df = create_result2_df(main_df)
rentals_by_day_date_df = create_rentals_by_day_date_df(main_df)

st.header('Bike Sharing Dashboard :sparkles:')

# Pertanyaan 1:
st.subheader('Trends Through the Seasons')
plt.figure(figsize=(10, 6))

# Plot untuk tahun 2011
plt.plot(result_df[result_df['yr'] == 2011]['season'],
         result_df[result_df['yr'] == 2011]['cnt'], label='2011')

# Plot untuk tahun 2012
plt.plot(result_df[result_df['yr'] == 2012]['season'],
         result_df[result_df['yr'] == 2012]['cnt'], label='2012')

plt.title('Total Rentals by Season (2011-2012)')
plt.xlabel('Season')
plt.ylabel('Total Rentals')
plt.legend()

# Menampilkan plot menggunakan Streamlit
st.pyplot(plt)

# Pertanyaan 2
st.subheader('Best Rental by The Weather')
# Membuat data untuk tahun 2011
data_2011 = result2_df[result2_df['year'] == 2011]
max_count_2011 = data_2011['total_rentals'].max()

# Membuat data untuk tahun 2012
data_2012 = result2_df[result2_df['year'] == 2012]
max_count_2012 = data_2012['total_rentals'].max()

# Membuat visualisasi dengan Streamlit
st.subheader('Total Bike Rentals by Weather Situation (2011)')
fig, ax = plt.subplots(figsize=(10, 6))
bars_2011 = ax.bar(data_2011['weathersit'], data_2011['total_rentals'], color=['green' if count == max_count_2011 else 'blue' for count in data_2011['total_rentals']])
ax.set_xlabel('Weather Situation')
ax.set_ylabel('Total Rentals')

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)

st.subheader('Total Bike Rentals by Weather Situation (2012)')
fig, ax = plt.subplots(figsize=(10, 6))
bars_2012 = ax.bar(data_2012['weathersit'], data_2012['total_rentals'], color=['green' if count == max_count_2012 else 'blue' for count in data_2012['total_rentals']])
ax.set_xlabel('Weather Situation')
ax.set_ylabel('Total Rentals')

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)

# Pertanyaan 3
st.subheader('Best Rental by Day Type')

# Membuat data untuk visualisasi
years = rentals_by_day_date_df['yr'].unique()
bar_width = 0.25
index = np.arange(len(years))

# Mencari hari dengan jumlah peminjaman sepeda tertinggi di setiap tahun
max_day_type_by_year = rentals_by_day_date_df.loc[rentals_by_day_date_df.groupby('yr')['cnt'].idxmax()]

# Membuat plot untuk setiap jenis hari
fig, ax = plt.subplots(figsize=(10, 6))

for i, year in enumerate(years):
    for j, day_type in enumerate(rentals_by_day_date_df['day_type'].unique()):
        color = 'red' if day_type == max_day_type_by_year[max_day_type_by_year['yr'] == year]['day_type'].values[0] else 'blue'
        data = rentals_by_day_date_df[(rentals_by_day_date_df['yr'] == year) & (rentals_by_day_date_df['day_type'] == day_type)]
        ax.bar(index[i] + j * bar_width, data['cnt'], bar_width, label=day_type, color=color)

        # Menambahkan nilai count di atas setiap bar
        ax.text(index[i] + j * bar_width, data['cnt'].values[0] + 1000, str(data['cnt'].values[0]), ha='center')

# Menambahkan legend
ax.legend()

ax.set_xlabel('Year')
ax.set_ylabel('Total Rentals')
ax.set_title('Total Bike Rentals by Day Type and Year')
ax.set_xticks(index + bar_width)
ax.set_xticklabels(years)

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig)


st.caption('Copyright (c) Nadira Maysa Dyandra 2024')