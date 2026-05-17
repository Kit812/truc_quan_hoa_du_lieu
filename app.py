import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN HỆ THỐNG (CHƯƠNG 4)
# ==========================================
st.set_page_config(
    page_title="Superstore BI Dashboard",
    page_icon="📊",
    layout="wide"
)

# Tiêu đề báo cáo chuẩn hóa theo Ngôn ngữ Doanh nghiệp
st.title("🖥️ EXECUTIVE BUSINESS INTELLIGENCE (BI) DASHBOARD")
st.markdown("## PHÂN TÍCH HIỆU SUẤT THƯƠNG MẠI & CHIẾN LƯỢC TỐI ƯU HÓA LỢI NHUẬN")
st.caption("Đồ án môn học: Trực quan hóa dữ liệu | Thực hiện bởi: Nhóm 14 - Lớp D22CNTT06")
st.markdown("---")

# ==========================================
# 2. KHỞI TẠO DỮ LIỆU GIẢ LẬP CHUẨN THỐNG KÊ (CHƯƠNG 3)
# ==========================================
@st.cache_data
def generate_perfect_superstore_data():
    np.random.seed(42)
    num_rows = 9994
    ship_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
    segments = ['Consumer', 'Corporate', 'Home Office']
    regions = ['West', 'East', 'Central', 'South']
    categories_map = {
        'Furniture': ['Chairs', 'Tables', 'Bookcases', 'Furnishings'],
        'Office Supplies': ['Storage', 'Binders', 'Paper', 'Art', 'Appliances', 'Labels', 'Envelopes', 'Fasteners', 'Supplies'],
        'Technology': ['Phones', 'Copiers', 'Accessories', 'Machines']
    }
    res_ship = np.random.choice(ship_modes, size=num_rows, p=[0.60, 0.20, 0.15, 0.05])
    res_seg = np.random.choice(segments, size=num_rows, p=[0.51, 0.30, 0.19])
    res_reg = np.random.choice(regions, size=num_rows, p=[0.32, 0.28, 0.23, 0.17])
    cats = list(categories_map.keys())
    res_cat = np.random.choice(cats, size=num_rows, p=[0.21, 0.60, 0.19])
    res_sub = []
    for c in res_cat:
        res_sub.append(np.random.choice(categories_map[c]))
    res_state = []
    for r in res_reg:
        if r == 'West': res_state.append(np.random.choice(['California', 'Washington']))
        elif r == 'East': res_state.append(np.random.choice(['New York', 'Pennsylvania', 'Ohio']))
        elif r == 'Central': res_state.append(np.random.choice(['Texas', 'Illinois', 'Michigan']))
        else: res_state.append(np.random.choice(['Florida', 'North Carolina']))

    res_sales = np.random.exponential(scale=175, size=num_rows) + 0.44
    res_sales = np.clip(res_sales, 0.44, 22638.48)
    res_sales[0] = 22638.48
    res_sales[10] = 15000.00
    res_sales[20] = 9000.00

    res_qty = np.random.randint(1, 15, size=num_rows)
    res_disc = np.random.choice([0.0, 0.2, 0.4, 0.7, 0.8], size=num_rows, p=[0.45, 0.30, 0.15, 0.06, 0.04])
    
    res_profit = []
    for i in range(num_rows):
        s = res_sales[i]
        d = res_disc[i]
        sub = res_sub[i]
        reg = res_reg[i]
        if d > 0.3:
            margin = -np.random.uniform(0.2, 0.8)
        else:
            margin = np.random.uniform(0.1, 0.4)
        if sub in ['Tables', 'Bookcases'] and reg in ['Central', 'South']:
            margin = -np.random.uniform(0.4, 1.2)
            res_disc[i] = max(res_disc[i], 0.4)
        if sub in ['Copiers', 'Phones']:
            margin = np.random.uniform(0.3, 0.5)
            res_disc[i] = min(res_disc[i], 0.2)
        res_profit.append(s * margin)
        
    res_profit = np.array(res_profit)
    res_profit = np.clip(res_profit, -6599.98, 8399.98)
    res_profit[5] = -6599.98
    res_profit[6] = 8399.98

    return pd.DataFrame({
        'Ship Mode': res_ship, 'Segment': res_seg, 'Region': res_reg,
        'State': res_state, 'Category': res_cat, 'Sub-Category': res_sub,
        'Sales': res_sales, 'Quantity': res_qty, 'Discount': res_disc, 'Profit': res_profit
    })

df = generate_perfect_superstore_data()

# ==========================================
# 3. MENU ĐIỀU KHIỂN & BỘ LỌC TƯƠNG TÁC (SIDEBAR)
# ==========================================
st.sidebar.markdown("### 🎛️ TRUNG TÂM ĐIỀU KHIỂN")
st.sidebar.markdown("---")

selected_region = st.sidebar.multiselect(
    "🌍 Phạm vi Địa lý (Region):",
    options=sorted(df['Region'].unique()), default=sorted(df['Region'].unique())
)

selected_segment = st.sidebar.multiselect(
    "👥 Phân khúc Thị trường (Segment):",
    options=sorted(df['Segment'].unique()), default=sorted(df['Segment'].unique())
)

selected_category = st.sidebar.multiselect(
    "📦 Danh mục Sản phẩm (Category):",
    options=sorted(df['Category'].unique()), default=sorted(df['Category'].unique())
)

selected_ship = st.sidebar.multiselect(
    "🚚 Phương thức Vận hành (Ship Mode):",
    options=sorted(df['Ship Mode'].unique()), default=sorted(df['Ship Mode'].unique())
)

# Áp dụng bộ lọc
filtered_df = df[
    (df['Region'].isin(selected_region)) & (df['Segment'].isin(selected_segment)) &
    (df['Category'].isin(selected_category)) & (df['Ship Mode'].isin(selected_ship))
]

if st.sidebar.button("🔄 Khởi động lại Bộ lọc"):
    st.rerun()

# ==========================================
# PHẦN I: CHỈ SỐ SỨC KHỎE DOANH NGHIỆP TRỌNG YẾU (KPI CARDS)
# ==========================================
st.header("I. CHỈ SỐ SỨC KHỎE DOANH NGHIỆP TRỌNG YẾU (CORE KPIs)")

t_sales = filtered_df['Sales'].sum()
t_profit = filtered_df['Profit'].sum()
t_orders = len(filtered_df)
p_margin = (t_profit / t_sales) * 100 if t_sales > 0 else 0
a_discount = filtered_df['Discount'].mean() * 100

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric(label="💰 Tổng doanh thu (Sales)", value=f"${t_sales:,.2f}")

if t_profit >= 0:
    kpi2.metric(label="📈 Lợi nhuận ròng (Profit)", value=f"${t_profit:,.2f}")
else:
    kpi2.metric(label="📉 Lợi nhuận ròng (Profit)", value=f"${t_profit:,.2f}", delta="Thua lỗ", delta_color="inverse")

if p_margin < 10:
    kpi3.metric(label="📊 Biên lợi nhuận (Margin)", value=f"{p_margin:.2f}%", delta="Cảnh báo biên độ thấp", delta_color="inverse")
else:
    kpi3.metric(label="📊 Biên lợi nhuận (Margin)", value=f"{p_margin:.2f}%", delta="Tỉ suất an toàn")

kpi4.metric(label="📦 Khối lượng giao dịch", value=f"{t_orders:,} Đơn")

if a_discount > 15:
    kpi5.metric(label="🚨 Tỉ lệ chiết khấu TB", value=f"{a_discount:.1f}%", delta="Vượt kiểm soát (>15%)", delta_color="inverse")
else:
    kpi5.metric(label="🚨 Tỉ lệ chiết khấu TB", value=f"{a_discount:.1f}%", delta="Mức an toàn")

st.markdown("---")

# ==========================================
# PHẦN II: PHÂN TÍCH CẤU TRÚC KINH DOANH SƠ BỘ
# ==========================================
st.header("II. PHÂN TÍCH CẤU TRÚC KINH DOANH TỔNG QUAN (DESCRIPTIVE ANALYSIS)")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("##### 📌 Top 10 Thị trường cấp Bang dẫn đầu Doanh thu")
    state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(10)
    fig_line = px.line(state_sales, x='State', y='Sales', labels={'State': 'Bang', 'Sales': 'Doanh thu (USD)'}, markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

with row1_col2:
    st.markdown("##### 📌 Tỉ trọng đóng góp Doanh thu theo Phân khúc Khách hàng")
    seg_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
    fig_pie = px.pie(seg_sales, values='Sales', names='Segment', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("##### 📌 Phân phối Doanh thu theo Khu vực địa lý & Danh mục Sản phẩm")
    reg_cat_sales = filtered_df.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
    fig_bar = px.bar(reg_cat_sales, x='Region', y='Sales', color='Category', barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_col2:
    st.markdown("##### 📌 Mô hình phân tán: Tác động của Chiết khấu đến Lợi nhuận")
    fig_scatter = px.scatter(filtered_df, x='Sales', y='Profit', color='Discount', color_continuous_scale='RdYlGn', opacity=0.5)
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ==========================================
# PHẦN III: DIAGNOSTIC MATRIX - ĐIỀU TRA NGUYÊN NHÂN THUA LỖ
# ==========================================
st.header("III. PHÂN TÍCH CHẨN ĐOÁN CHIÊN SÂU (DIAGNOSTIC MATRIX & RISK DETECTION)")
st.caption("Ứng dụng cấu trúc phân cấp trực quan nâng cao để định vị các điểm nóng (Hotspots) ảnh hưởng tiêu cực đến dòng tiền.")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.markdown("##### 🧬 Ma trận nhiệt: Hiệu suất sinh lời trung bình (Region vs Category)")
    heat_data = filtered_df.groupby(['Region', 'Category'])['Profit'].mean().reset_index()
    heat_pivot = heat_data.pivot(index='Region', columns='Category', values='Profit')
    fig_heatmap = px.imshow(fig_heatmap := heat_pivot, color_continuous_scale='RdYlGn', color_continuous_midpoint=0, text_auto=".1f")
    st.plotly_chart(fig_heatmap, use_container_width=True)

with row3_col2:
    st.markdown("##### 🧬 Biểu đồ phân cấp Cây (Treemap): Cơ cấu rủi ro theo Danh mục phụ")
    fig_treemap = px.treemap(filtered_df, path=['Category', 'Sub-Category'], values='Sales', color='Profit', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
    fig_treemap.update_traces(hovertemplate="<b>Phân loại:</b> %{label}<br><b>Doanh thu:</b> $%{value:,.2f}<br><b>Lợi nhuận:</b> $%{color:,.2f}<extra></extra>")
    st.plotly_chart(fig_treemap, use_container_width=True)

# ==========================================
# PHẦN IV: DATA AUDIT LOG & INSIGHTS
# ==========================================
st.markdown("---")
st.header("IV. ĐỐI SOÁT DỮ LIỆU GIAO DỊCH CHI TIẾT (DATA AUDIT LOG)")
st.dataframe(
    filtered_df.sort_values(by="Profit", ascending=True),
    use_container_width=True,
    column_config={
        "Sales": st.column_config.NumberColumn("Doanh thu", format="$%,.2f"),
        "Profit": st.column_config.NumberColumn("Lợi nhuận ròng", format="$%,.2f")
    }
)
