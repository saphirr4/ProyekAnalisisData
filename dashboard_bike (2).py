# -*- coding: utf-8 -*-
"""dashboard bike.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xGHxeq_Qd7xuUQCOixZ8C7TFooW4K924

## Menyiapkan DataFrame
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

bike_df = pd.read_csv("https://raw.githubusercontent.com/saphirr4/ProyekAnalisisData/main/bike_data.csv")

"""### Menyiapkan daily_users_df"""

def create_daily_users_df(df):
    daily_users_df = df.resample(rule='D', on='dteday_x').agg({
        "instant": "nunique",
        "cnt_x": "sum"
    })
    daily_users_df = daily_users_df.reset_index()
    daily_users_df.rename(columns={
        "instant": "instant_count",
        "cnt_x": "jumlah peminjaman"
    }, inplace=True)

    return daily_users_df

"""### Menyiapkan byseason_df"""

def create_byseason_df(df):
    byseason_df = df.groupby(by="season_x").instant.nunique().reset_index()
    byseason_df.rename(columns={
        "instant": "instant_count"
    }, inplace=True)

    return byseason_df

"""### Menyiapkan byworkingday_df"""

def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by="workingday_x")['cnt_x'].sum().reset_index()
    byworkingday_df.rename(columns={
        "instant": "instant_count"
    }, inplace=True)

    return byworkingday_df

"""### Menyiapkan byhumwind_df"""

def create_byhumwind_df(df):
    byhumwind_df = df.groupby(['hum_x', 'windspeed_x'])['cnt_x'].sum().reset_index()
    byhumwind_df.rename(columns={
        "instant": "instant_count"
    }, inplace=True)

    return byhumwind_df

"""### Menyiapkan rfm_df"""

def create_rfm_df(df):
  rfm_df = bike_df.groupby(by="instant", as_index=False).agg({
    "dteday_x": "max", # tanggal peminjaman terakhir
    "instant": "nunique", # jumlah peminjaman
    "cnt_x": "sum" # menghitung jumlah users
    })
  rfm_df.columns = ["max_dteday_x", "frequency", "monetary"]
  # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
  rfm_df["max_dteday_x"] = pd.to_datetime(rfm_df["max_dteday_x"])
  recent_date = bike_df["dteday_y"].max()
  rfm_df["recency"] = (recent_date - rfm_df["max_dteday_x"]).dt.days

  rfm_df.drop("max_dteday_x", axis=1, inplace=True)
  rfm_df.head()

  return rfm_df

"""## Mengurutkan DataFrame"""

datetime_columns = ["dteday_x","dteday_y"]
bike_df.sort_values(by="dteday_x", inplace=True)
bike_df.reset_index(inplace=True)

for column in datetime_columns:
    bike_df[column] = pd.to_datetime(bike_df[column])

"""## Membuat Komponen Filter"""

min_date = bike_df["dteday_x"].min()
max_date = bike_df["dteday_x"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("/content/8859498-removebg-preview.png")
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = bike_df[(bike_df["dteday_x"] >= str(start_date)) &
                (bike_df["dteday_x"] <= str(end_date))]

daily_users_df = create_daily_users_df(main_df)
byseason_df = create_byseason_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byhumwind_df = create_byhumwind_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Bike Sharing System')

st.subheader('Demografi Pelanggan')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(30, 20))

    sns.barplot(
        y="instant_count",
        x="season_x",
        data=byseason_df.sort_values(by="instant_count", ascending=False),
        ax=ax
    )
    ax.set_title("Jumlah Peminjaman Sepeda berdasarkan Musim", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(30, 20))

    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="cnt_x",
        x="workingday_x",
        data=byworkingday_df.sort_values(by="cnt_x", ascending=False),
        ax=ax
    )
    ax.set_title("Jumlah Peminjaman Sepeda berdasarkan Jenis Hari", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

st.subheader('Demografi Pelanggan Lainnya')

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(30, 20))

    sns.barplot(
        y="cnt_x",
        x="hum_x",
        data=byhumwind_df.sort_values(by="cnt_x", ascending=False),
        ax=ax
    )
    ax.set_title("Jumlah Peminjaman Sepeda berdasarkan Kelembaban", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(30, 20))

    colors = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="cnt_x",
        x="windspeed_x",
        data=byhumwind_df.sort_values(by="cnt_x", ascending=False),
        ax=ax
    )
    ax.set_title("Jumlah Peminjaman Sepeda berdasarkan Kecepatan Angin", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

    st.caption('Copyright © Dicoding 2023')

"""## Cek Requirements.txt

"""

from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

"""## Install requirements.txt"""

!pip install -r /content/requirements.txt