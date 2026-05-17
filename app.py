import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Cấu hình trang Dashboard (Đồng bộ font hệ thống Streamlit)
st.set_page_config(
    page_title="Superstore Sales & Profit Dashboard",
    page_icon="📊",
    layout="wide"
)

# Tiêu đề Dashboard
st.title("📊 Hệ Thống Phân Tích Dữ Liệu Bán Hàng & Tối Ưu Hóa Lợi Nhuận")
st.markdown("### Chuỗi cửa hàng Superstore")
st.markdown("---")

# 2. Giả lập/Tải dữ liệu (Đảm bảo cấu trúc chính xác theo đồ án)
@st.cache_data
def load_data():
    # Trong thực tế, bạn sẽ dùng: pd.read_csv("Sample_Superstore.csv")
    # Dưới đây là dữ liệu giả lập chuẩn cấu trúc bài làm của bạn để test giao diện
    data = {
        'Category': ['Furniture', 'Furniture', 'Office Supplies', 'Office Supplies', 'Technology', 'Technology']*4,
        'Sub-Category': ['Chairs', 'Tables', 'Storage', 'Binders', 'Phones', 'Copiers', 
                        'Bookcases', 'Furnishings', 'Art', 'Paper', 'Accessories', 'Machines']*2,
        'Region': ['West', 'East', 'Central', 'South']*6,
        'Sales': [12000, 8000, 5000, 3000, 15000, 22000, 6000, 2500, 1500, 1200, 7000, 11000]*2,
        'Profit': [1800, -2500, 600, 400, 2500, 4500, -1200, 300, 200, 150, 900, -800]*2,
        'Quantity': [45, 30, 80, 120, 50, 15, 20, 60, 95, 150, 40, 10]*2
    }
    return pd.DataFrame(data)

df = load_data()

# 3. THANH BỘ LỌC (SIDEBAR) - Tăng tính tương tác theo yêu cầu kiểm thử
st.sidebar.header("🎛️ Bộ Lọc Tương Tác")
selected_region = st.sidebar.multiselect(
    "Chọn Khu Vực (Region):",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

selected_category = st.sidebar.multiselect(
    "Chọn Danh Mục Chính (Category):",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Lọc dữ liệu theo lựa chọn của người dùng
filtered_df = df[(df['Region'].isin(selected_region)) & (df['Category'].isin(selected_category))]

# 4. HỒI 1: TỔNG QUAN (KPI Cards) - Đồng bộ màu sắc cảnh báo lỗ/lãi
st.subheader("📍 Hồi 1: Số Liệu Tổng Quan (KPIs)")
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_quantity = filtered_df['Quantity'].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="💰 Tổng Doanh Thu (Sales)", value=f"${total_sales:,.2f}")

# Cảnh báo màu đỏ nếu Lợi nhuận âm, màu xanh nếu dương
if total_profit >= 0:
    col2.metric(label="📈 Tổng Lợi Nhuận (Profit)", value=f"${total_profit:,.2f}", delta=f"{profit_margin:.2f}% Margin")
else:
    col2.metric(label="📉 Tổng Lợi Nhuận (Profit)", value=f"${total_profit:,.2f}", delta=f"{profit_margin:.2f}% Margin", delta_color="inverse")

col3.metric(label="📦 Số Lượng Đã Bán", value=f"{total_quantity:,} sp")
col4.metric(label="🗺️ Số Khu Vực Đang Chọn", value=f"{len(selected_region)}/{len(df['Region'].unique())}")

st.markdown("---")

# 5. HỒI 2 & 3: PHÂN TÍCH SÂU VÙNG ĐỎ LỖ/LÃI (Treemap & Heatmap nâng cao)
st.subheader("🔍 Hồi 2 & 3: Phân Tích Chuyên Sâu Tối Ưu Lợi Nhuận")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 🌳 Biểu đồ Treemap: Cơ Cấu Doanh Thu & Lợi Nhuận")
    st.caption("Kích thước ô = Doanh thu | Màu sắc = Lợi nhuận (Áp dụng thang màu RdYlGn để bắt 'vùng đỏ' thua lỗ)")
    
    # Tạo biểu đồ Treemap theo cấu trúc cây: Category -> Sub-Category
    # Áp dụng cải tiến từ User Testing: Custom hovertemplate để giao diện gọn gàng, trực quan
    fig_tree = px.treemap(
        filtered_df, 
        path=['Category', 'Sub-Category'], 
        values='Sales',
        color='Profit',
        color_continuous_scale='RdYlGn',  # Thang màu Đỏ (Lỗ) - Vàng (Hòa) - Xanh (Lãi) chuẩn đồ án
        color_continuous_midpoint=0
    )
    
    fig_tree.update_traces(
        hovertemplate="<b>Phân loại:</b> %{label}<br><b>Doanh thu:</b> $%{value:,.2f}<br><b>Lợi nhuận:</b> $%{color:,.2f}<extra></extra>"
    )
    fig_tree.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)

with col_right:
    st.markdown("#### 🗺️ Biểu đồ Heatmap: Ma Trận Lợi Nhuận Theo Khu Vực")
    st.caption("Cải tiến hiển thị: Tự động hiển thị số tiền trực tiếp trên các ô dữ liệu")
    
    # Nhóm dữ liệu để làm ma trận Heatmap (Trục X: Khu vực, Trục Y: Phân loại phụ)
    pivot_df = filtered_df.groupby(['Sub-Category', 'Region'])['Profit'].sum().reset_index()
    pivot_matrix = pivot_df.pivot(index='Sub-Category', columns='Region', values='Profit').fillna(0)
    
    # Áp dụng cải tiến quan trọng nhất từ User Testing: text_auto=True để hiện thẳng số USD
    fig_heat = px.imshow(
        pivot_matrix,
        labels=dict(x="Khu Vực (Region)", y="Sản Phẩm Phụ (Sub-Category)", color="Lợi Nhuận ($)"),
        x=pivot_matrix.columns,
        y=pivot_matrix.index,
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        text_auto=".0f" # Hiển thị số nguyên trực tiếp trên ô (Ví dụ: -2500)
    )
    fig_heat.update_layout(margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

st.markdown("---")

# 6. BẢNG DỮ LIỆU CHI TIẾT (Dành cho việc đối soát số liệu nhanh)
st.subheader("📋 Bảng Tra Cứu Dữ Liệu Tinh Gọn")
st.dataframe(
    filtered_df.sort_values(by="Profit", ascending=True), 
    use_container_width=True,
    column_config={
        "Sales": st.column_config.NumberColumn("Doanh Thu", format="$%,.2f"),
        "Profit": st.column_config.NumberColumn("Lợi Nhuận", format="$%,.2f"),
        "Quantity": st.column_config.NumberColumn("Số Lượng")
    }
)

# Chú thích cuối trang phản ánh hạn chế bộ dữ liệu như mô tả trong Chương 5
st.info("💡 **Ghi chú kỹ thuật:** Dashboard hiện tại tối ưu hóa phân tích tĩnh theo Không gian (Khu vực/Danh mục). Khía cạnh phân tích Thời gian (Time-series) chưa được tích hợp do giới hạn thuộc tính thuộc dữ liệu gốc.")
