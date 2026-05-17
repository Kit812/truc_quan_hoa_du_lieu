import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CẤU HÌNH TRANG & GIAO DIỆN
st.set_page_config(
    page_title="Superstore Sales & Profit Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Phong cách CSS tối ưu hiển thị và màu sắc
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
    div[data-testid="stMetricValue"] {font-size: 24px; font-weight: bold;}
    .kpi-box {text-align: center; padding: 10px; border-radius: 5px; margin: 5px;}
    </style>
""", unsafe_allow_html=True)

# 2. MÔ PHỎNG DỮ LIỆU CHUẨN (Bảo toàn cấu trúc 9,994 dòng để chạy thực tế)
@st.cache_data
def load_data():
    # Trong thực tế, thay thế bằng: pd.read_csv("SampleSuperstore.csv")
    # Dưới đây tạo dữ liệu mô phỏng chuẩn theo đúng thống kê mô tả trong báo cáo
    import numpy as np
    np.random.seed(42)
    n = 9994
    
    states = ['California', 'New York', 'Texas', 'Washington', 'Pennsylvania', 'Florida', 'Illinois', 'Ohio', 'Michigan', 'North Carolina'] + ['Other']*39
    regions = ['West', 'East', 'Central', 'South']
    segments = ['Consumer', 'Corporate', 'Home Office']
    categories = ['Furniture', 'Office Supplies', 'Technology']
    sub_cats = {
        'Furniture': ['Tables', 'Chairs', 'Bookcases', 'Furnishings'],
        'Office Supplies': ['Binders', 'Paper', 'Storage', 'Art', 'Appliances', 'Labels', 'Envelopes', 'Fasteners', 'Supplies'],
        'Technology': ['Phones', 'Copiers', 'Accessories', 'Machines']
    }
    ship_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
    
    data = []
    for _ in range(n):
        reg = np.random.choice(regions, p=[0.32, 0.28, 0.22, 0.18]) # West & East chiếm ưu thế
        seg = np.random.choice(segments, p=[0.51, 0.30, 0.19])     # Theo Pie chart báo cáo
        cat = np.random.choice(categories, p=[0.21, 0.60, 0.19])
        sub_c = np.random.choice(sub_cats[cat])
        state = np.random.choice(states)
        sm = np.random.choice(ship_modes)
        qty = int(np.random.randint(1, 15))
        
        # Thiết lập logic chiết khấu và lợi nhuận theo câu chuyện dữ liệu
        disc = np.random.choice([0.0, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8], p=[0.4, 0.1, 0.2, 0.1, 0.1, 0.05, 0.05])
        
        # Thách thức thực tế: Lỗ nặng ở Furniture/Tables và khu vực Central nếu discount cao
        if cat == 'Furniture' and sub_c == 'Tables' and reg == 'Central':
            disc = np.random.choice([0.4, 0.6, 0.8])
            
        sales = float(np.random.exponential(scale=200) + 0.44)
        if disc > 0.3:
            profit = float(-sales * np.random.uniform(0.2, 0.8)) # Chiết khấu cao -> Lỗ nặng
        else:
            profit = float(sales * np.random.uniform(0.05, 0.35))
            
        data.append([sm, seg, state, reg, cat, sub_c, sales, qty, disc, profit])
        
    df = pd.DataFrame(data, columns=['Ship Mode', 'Segment', 'State', 'Region', 'Category', 'Sub-Category', 'Sales', 'Quantity', 'Discount', 'Profit'])
    
    # Tiền xử lý dữ liệu chuẩn hóa như báo cáo mô tả
    df['Ship Mode'] = df['Ship Mode'].str.strip()
    df['Segment'] = df['Segment'].str.strip()
    df['Category'] = df['Category'].str.strip()
    df['Sub-Category'] = df['Sub-Category'].str.strip()
    return df

df = load_data()

# 3. THANH SIDEBAR - BỘ LỌC TƯƠNG TÁC (SLICERS)
st.sidebar.header("Bộ Lọc Tương Tác")

# Tránh mất bộ lọc khi reset bằng multiselect mặc định trống là chọn tất cả
region_sel = st.sidebar.multiselect("Khu vực (Region)", options=sorted(df['Region'].unique()), default=df['Region'].unique())
segment_sel = st.sidebar.multiselect("Phân khúc (Segment)", options=sorted(df['Segment'].unique()), default=df['Segment'].unique())
category_sel = st.sidebar.multiselect("Danh mục (Category)", options=sorted(df['Category'].unique()), default=df['Category'].unique())
ship_sel = st.sidebar.multiselect("Phương thức vận chuyển (Ship Mode)", options=sorted(df['Ship Mode'].unique()), default=df['Ship Mode'].unique())

if st.sidebar.button("Reset Bộ Lọc"):
    st.rerun()

# Áp dụng bộ lọc động vào DataFrame
df_filtered = df[
    (df['Region'].isin(region_sel)) &
    (df['Segment'].isin(segment_sel)) &
    (df['Category'].isin(category_sel)) &
    (df['Ship Mode'].isin(ship_sel))
]

# TÌM TRẠNG THÁI HIỂN THỊ CẢNH BÁO CHO KPI BIÊN LỢI NHUẬN
total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
total_orders = len(df_filtered)
avg_discount = df_filtered['Discount'].mean() * 100

# Quyết định màu sắc động của biên lợi nhuận (Mục 4.2.2)
if profit_margin < 10:
    margin_color = "#FF4B4B" # Đỏ
elif profit_margin <= 20:
    margin_color = "#FFAA00" # Vàng
else:
    margin_color = "#00B050" # Xanh lá

# 4. VÙNG HIỂN THỊ CHÍNH (MAIN AREA)
st.title("📊 Phân Tích & Trực Quan Hóa Dữ Liệu Bán Hàng Superstore")
st.caption("Đồ án môn học Trực quan hóa dữ liệu — Nhóm 14 — D22CNTT06")

# ---- TẦNG 1: HỆ THỐNG KPI CARDS ----
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Sales", f"${total_sales:,.2f}")

if total_profit < 0:
    kpi2.markdown(f"<div class='kpi-box' style='background-color:#FFEBEB; color:#FF4B4B;'><strong>Total Profit</strong><br><span style='font-size:24px;'>-${abs(total_profit):,.2f}</span></div>", unsafe_allow_html=True)
else:
    kpi2.metric("Total Profit", f"${total_profit:,.2f}")

kpi3.markdown(f"<div class='kpi-box' style='background-color:#F0F2F6; color:{margin_color};'><strong>Profit Margin</strong><br><span style='font-size:24px;'>{profit_margin:.2f}%</span></div>", unsafe_allow_html=True)
kpi4.metric("Total Orders", f"{total_orders:,} đơn")
kpi5.metric("Avg. Discount", f"{avg_discount:.2f}%", delta="- Ngưỡng nguy hiểm >30%" if avg_discount > 30 else None, delta_color="inverse")

st.write("---")

# ---- TẦNG 2: HỆ THỐNG BIỂU ĐỒ CƠ BẢN ----
st.subheader("Ý hồi 1 & 2: Hệ thống biểu đồ cơ bản khám phá dữ liệu")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # 3.4.1. Line Graph Top 10 bang dẫn đầu doanh thu
    state_sales = df_filtered.groupby('State')['Sales'].sum().reset_index()
    top10_states = state_sales.sort_values(by='Sales', ascending=False).head(10)
    fig_line = px.line(
        top10_states, x='State', y='Sales', text=top10_states['Sales'].map(lambda x: f"${x:,.0f}"),
        title="Top 10 Bang Dẫn Đầu Doanh Thu (USD)", labels={'Sales': 'Doanh Thu (USD)', 'State': 'Bang'},
        markers=True
    )
    fig_line.update_traces(textposition="top center", line_color="#1F77B4")
    st.plotly_chart(fig_line, use_container_width=True)

    # 3.4.3. Stacked Bar Chart Doanh thu theo khu vực và danh mục
    region_cat_sales = df_filtered.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
    fig_stacked = px.bar(
        region_cat_sales, x='Region', y='Sales', color='Category',
        title="Doanh Thu Theo Khu Vực Và Danh Mục Sản Phẩm",
        labels={'Sales': 'Doanh Thu (USD)', 'Region': 'Khu Vực'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_stacked, use_container_width=True)

with col_chart2:
    # 3.4.2. Pie Chart Tỷ trọng doanh thu theo phân khúc khách hàng
    segment_sales = df_filtered.groupby('Segment')['Sales'].sum().reset_index()
    fig_pie = px.pie(
        segment_sales, values='Sales', names='Segment', hole=0.3,
        title="Tỷ Trọng Doanh Thu Theo Phân Khúc Khách Hàng",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

    # 3.4.4. Scatter Plot Tương quan giữa Doanh thu, Lợi nhuận và Chiết khấu
    fig_scatter = px.scatter(
        df_filtered, x='Sales', y='Profit', color='Discount', opacity=0.5,
        title="Tương Quan Giữa Doanh Thu, Lợi Nhuận Và Chiết Khấu",
        labels={'Sales': 'Doanh Thu (USD)', 'Profit': 'Lợi Nhuận (USD)'},
        color_continuous_scale=px.colors.sequential.RdBu_r
    )
    # Thêm đường tham chiếu Profit = 0
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black", opacity=0.7)
    st.plotly_chart(fig_scatter, use_container_width=True)

st.write("---")

# ---- TẦNG 3: HỆ THỐNG BIỂU ĐỒ NÂNG CAO (ĐÃ CẢI TIẾN) ----
st.subheader("Ý hồi 3: Hệ thống biểu đồ nâng cao vạch trần rủi ro")
col_adv1, col_adv2 = st.columns(2)

with col_adv1:
    # 3.5.1. Heatmap Lợi nhuận trung bình theo Khu vực & Danh mục (Cải tiến tăng tương phản và text auto)
    pivot_heatmap = df_filtered.pivot_table(index='Region', columns='Category', values='Profit', aggfunc='mean').round(2)
    
    fig_heatmap = px.imshow(
        pivot_heatmap,
        text_auto='.2f', # HIỂN THỊ NHÃN GIÁ TRỊ TRỰC TIẾP TRONG Ô (Cải tiến 2)
        color_continuous_scale='RdYlGn', # THANG MÀU TƯƠNG PHẢN CAO ĐỎ - VÀNG - XANH (Cải tiến 2)
        title="Heatmap: Lợi Nhuận Trung Bình Theo Khu Vực Và Danh Mục",
        labels=dict(x="Danh Mục Sản Phẩm", y="Khu Vực", color="Lợi Nhuận TB (USD)")
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col_adv2:
    # 3.5.2. Treemap Phân cấp cấu trúc Category -> Sub-Category (Cải tiến tùy chỉnh hovertemplate)
    df_tree = df_filtered.groupby(['Category', 'Sub-Category']).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    
    fig_treemap = px.treemap(
        df_tree, 
        path=['Category', 'Sub-Category'], 
        values='Sales',
        color='Profit',
        color_continuous_scale='RdYlGn',
        title="Treemap: Phân Cấp Danh Mục Theo Quy Mô Doanh Thu & Biên Độ Lợi Nhuận"
    )
    
    # TÙY CHỈNH HOVER TOOLTIP CHI TIẾT (Cải tiến 1 từ User testing)
    fig_treemap.update_traces(
        hovertemplate="<b>Phân loại:</b> %{label}<br><b>Tổng Doanh Thu (Diện tích):</b> $%{value:,.2f}<br><b>Tổng Lợi Nhuận (Màu sắc):</b> $%{color:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)
