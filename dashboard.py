import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Fungsi untuk membuat daily_orders_df yang benar
def create_daily_orders_df(df):
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",  # Menghitung jumlah order unik per hari
        "price": "sum"          # Menjumlahkan total pendapatan (revenue) per hari
    }).reset_index()
    
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

# Fungsi untuk mendapatkan produk dengan penjualan tertinggi & terendah
def get_top_bottom_products(df, column_name="product_category_name", sales_column="order_item_id", top_n=5):
    if column_name not in df.columns:
        if "product_name" in df.columns:
            df[column_name] = df["product_name"]
        else:
            raise ValueError(f"Kolom '{column_name}' atau 'product_name' tidak ditemukan dalam DataFrame.")

    if sales_column not in df.columns:
        raise ValueError(f"Kolom '{sales_column}' tidak ditemukan dalam DataFrame.")

    df_sorted = df.sort_values(by=sales_column, ascending=False).reset_index(drop=True)

    top_products = df_sorted.head(top_n)
    bottom_products = df_sorted.tail(top_n)

    return top_products, bottom_products

# Membaca dataset
all_df = pd.read_csv("all_data.csv")

# Pastikan kolom datetime diformat dengan benar
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

# Menentukan rentang tanggal
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

# Sidebar Streamlit
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

# Filter data berdasarkan rentang tanggal yang dipilih
main_df = all_df[
    (all_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & 
    (all_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]

# Membuat daily_orders_df dari data yang sudah difilter
daily_orders_df = create_daily_orders_df(main_df)

# ✅ Membuat sum_order_items_df sebelum dipanggil
sum_order_items_df = main_df.groupby("product_category_name")["order_item_id"].sum().reset_index()

# ✅ Sekarang bisa memanggil fungsi
top_5_products, bottom_5_products = get_top_bottom_products(sum_order_items_df, top_n=5)

# Streamlit Header
st.header('Dicoding Collection Dashboard :sparkles:')
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

st.subheader("Best & Worst Performing Product")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
 
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
 
sns.barplot(x="order_item_id", y="product_category_name", data=sum_order_items_df.sort_values(by="order_item_id", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
 
st.pyplot(fig)