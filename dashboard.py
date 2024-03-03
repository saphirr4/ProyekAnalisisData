import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

all_df = pd.read_csv("https://raw.githubusercontent.com/amelanandaa/Tugas-Akhir-Dicoding/main/all_data_ecommerce.csv")

#sort berdasarkan tanggal
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
all_df.sort_values(by="order_purchase_timestamp", inplace=True)

#membuat fungsi dari order
def create_order_df(df):
  total_order_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
      "order_id":"nunique",
      "payment_value":"sum",
      "product_id":"nunique"
  })
  total_order_df = total_order_df.reset_index()
  total_order_df.rename(columns={
      "order_id":"order_count",
      "payment_value":"revenue",
      "product_id":"product_count"
  }, inplace=True)

  return total_order_df

#membuat fungsi RFM
def create_rfm(df):
  rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
    "order_purchase_timestamp" : "max",
    "order_id":"nunique",
    "payment_value":"sum"
  })
  rfm_df.columns = ["customer_id","max_order","frequency","monatary"]

  rfm_df["max_order"]= rfm_df["max_order"].dt.date
  recent = all_df["order_purchase_timestamp"].dt.date.max()
  rfm_df["recency"] = rfm_df["max_order"].apply(lambda x: (recent - x).days)

  rfm_df.drop("max_order", axis=1, inplace =True)
  rfm_df["customer_id"] = rfm_df["customer_id"].astype(str)  # Konversi ke tipe string
  rfm_df["customer_id"] = rfm_df["customer_id"].str[:4]      # Mengambil 4 digit pertama dari id
  return rfm_df
  
total_order_df = create_order_df(all_df)
rfm_df = create_rfm(all_df)

st.header("Dashboard E-commerce")
#untuk menginput nama
name = st.text_input(label="Nama", value='')
st.write('Hallo ', name, ', selamat datang di dashboard kami')

col1, col2, col3 = st.columns(3)
with col1:
  jumlah_order = total_order_df.order_count.sum()
  st.metric("Total Order", value=jumlah_order)

with col2:
  total_product = total_order_df.product_count.sum()
  st.metric("Total Produk", value=total_product)

with col3:
  total_revenue = format_currency(total_order_df.revenue.sum(), "USD", locale='en_US')
  st.metric("Total Pendapatan", value=total_revenue)

# produk dengan pembelian terbanyak dan tersedikit
st.subheader("Produk Terjual")
fig, ax = plt.subplots(ncols=2, figsize=(15,5))

#plot pertama
product_order = all_df.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=False)
top_5_product = product_order.head(5)
ax[0].bar(top_5_product.index, top_5_product, color="skyblue")
ax[0].set_title('5 Produk Teratas')
ax[0].tick_params(axis='x', rotation=45)

#plot kedua
product_order_low = all_df.groupby("product_category_name_english").order_id.nunique().sort_values(ascending=True)
low_5_product = product_order_low.head(5)
ax[1].bar(low_5_product.index, low_5_product, color="skyblue")
ax[1].set_title('5 Produk Terendah')
ax[1].tick_params(axis='x', rotation=45)

st.pyplot(fig)


st.subheader("Pendapatan dan Order Berdasarkan Bulan")
fig, ax = plt.subplots(figsize=(15,5))
monthly = all_df.resample(rule='M', on="order_purchase_timestamp").agg({
    "order_id":"nunique",
    "payment_value":"sum"
})
monthly.index = monthly.index.strftime('%Y-%m')
ax.plot( monthly.index, monthly["payment_value"], color="#72BCD4")
ax.set_title("Total Pendapatan Perbulan")
ax.set_xlabel('Date', fontsize=10)
ax.set_ylabel('Revenue',fontsize=10)
ax.tick_params(rotation=45)

st.pyplot(fig)

#RFM Analysis
st.subheader("RFM Analysis")
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35,8))
colors = ["#72BCD4","#72BCD4","#72BCD4","#72BCD4","#72BCD4"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency", loc="center", fontsize=35)
ax[0].tick_params(axis ='x', labelsize=30, rotation=45)
ax[0].tick_params(axis='y', labelsize=30)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=35)
ax[1].tick_params(axis='x', labelsize=30, rotation=45)
ax[1].tick_params(axis='y', labelsize=30)

sns.barplot(y="monatary", x="customer_id", data=rfm_df.sort_values(by="monatary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=35)
ax[2].tick_params(axis='x', labelsize=30, rotation=45)
ax[0].tick_params(axis='y', labelsize=30)

st.pyplot(fig)
