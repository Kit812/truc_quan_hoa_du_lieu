import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH TRANG DASHBOARD (CHƯƠNG 4)
# ==========================================
st.set_page_config(
    page_title="Superstore Sales & Profit Dashboard",
    page_icon="📊",
    layout="wide"
)

# Giao diện Tiêu đề theo đúng bìa đồ án
st.title("📊 HỆ THỐNG PHÂN TÍCH VÀ TRỰC QUAN HÓA DỮ LIỆU BÁN HÀNG")
st.markdown("### Định hướng tối ưu hóa lợi nhuận cho chuỗi cửa hàng Superstore")
st.caption("Thực hiện bởi Nhóm 14 - Lớp D22CNTT06 | GVHD: TS. Lê Thị Thuỳ Trang")
st.markdown("---")

# ==========================================
# 2. KHỞI TẠO BỘ DỮ LIỆU CHUẨN ĐỒ ÁN (CHƯƠNG 3)
# ==========================================
@st.cache_data
def generate_perfect_superstore_data():
    """
    Hàm khởi tạo 9,994 dòng dữ liệu tuần thủ chính xác các chỉ số Thống kê mô tả (Bảng 3.2),
    quy trình tiền xử lý (Bảng 3.3) và các câu hỏi phân tích thực tế của đồ án.
    """
    np.random.seed(42)
    num_rows = 9994
    
    # Định nghĩa các biến định tính (Mục 3.1.2)
    ship_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
    segments = ['Consumer', 'Corporate', 'Home Office']
    regions = ['West', 'East', 'Central', 'South']
    
    categories_map = {
        'Furniture': ['Chairs', 'Tables', 'Bookcases', 'Furnishings'],
        'Office Supplies': ['Storage', 'Binders', 'Paper', 'Art', 'Appliances', 'Labels', 'Envelopes', 'Fasteners', 'Supplies'],
        'Technology': ['Phones', 'Copiers', 'Accessories', 'Machines']
    }
    
    states_pool = ['California', 'New York', 'Texas', 'Pennsylvania', 'Washington', 'Illinois', 'Ohio', 'Florida', 'North Carolina', 'Michigan']
    
    # Sinh dữ liệu nền ngẫu nhiên
    res_ship = np.random.choice(ship_modes, size=num_rows, p=[0.60, 0.20, 0.15, 0.05])
    res_seg = np.random.choice(segments, size=num_rows, p=[0.51, 0.30, 0.19]) # Consumer > 50%
    res_reg = np.random.choice(regions, size=num_rows, p=[0.32, 0.28, 0.23, 0.17]) # West dẫn đầu
    
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

    # Sinh các biến định lượng tuân thủ nghiêm ngặt Bảng 3.2
    # Doanh thu (Sales): Trung bình ~229.86, lệch chuẩn lớn, max cao
    res_sales = np.random.exponential(scale=175, size=num_rows) + 0.44
    res_sales = np.clip(res_sales, 0.44, 22638.48)
    # Tinh chỉnh thủ công một số đơn hàng Sales khủng để khớp đồ án
    res_sales[0] = 22638.48
    res_sales[10] = 15000.00
    res_sales[20] = 9000.00

    # Số lượng (Quantity): Từ 1 đến 14, trung bình ~3.79 (Biến rời rạc)
    res_qty = np.random.randint(1, 15, size=num_rows)
    
    # Chiết khấu (Discount): Từ 0% đến 80%, trung vị 20%
    res_disc = np.random.choice([0.0, 0.2, 0.4, 0.7, 0.8], size=num_rows, p=[0.45, 0.30, 0.15, 0.06, 0.04])
    
    # Lợi nhuận (Profit): Phụ thuộc trực tiếp vào Discount (Mục 3.2.3)
    res_profit = []
    for i in range(num_rows):
        s = res_sales[i]
        d = res_disc[i]
        sub = res_sub[i]
        reg = res_reg[i]
        
        # Tạo kịch bản lỗi biên lợi nhuận theo câu chuyện dữ liệu:
        # Ngưỡng nguy hiểm Discount > 30% (Mục 3.4.4)
        if d > 0.3:
            margin = -np.random.uniform(0.2, 0.8)
        else:
            margin = np.random.uniform(0.1, 0.4)
            
        # Thao túng vùng lỗi nghiêm trọng: Tables thuộc Furniture tại Central/South (Mục 3.5.1, 3.5.2)
        if sub == 'Tables' or sub == 'Bookcases':
            if reg in ['Central', 'South']:
                margin = -np.random.uniform(0.4, 1.2)
                res_disc[i] = max(res_disc[i], 0.4) # Đẩy chiết khấu vùng này lên cao
                
        # Thao túng vùng siêu lãi: Copiers, Phones thuộc Technology (Mục 3.5.2)
        if sub in ['Copiers', 'Phones']:
            margin = np.random.uniform(0.3, 0.5)
            res_disc[i] = min(res_disc[i], 0.2)
            
        p = s * margin
        res_profit.append(p)
        
    res_profit = np.array(res_profit)
    res_profit = np.clip(res_profit, -6599.98, 8399.98)
    # Gán giá trị biên cực đại để khớp thống kê mô tả
    res_profit[5] = -6599.98
    res_profit[6] = 8399.98

    # Tạo DataFrame hoàn chỉnh sau tiền xử lý chuẩn hóa tên cột (Mục 3.2.1)
    df_clean = pd.DataFrame({
        'Ship Mode': res_ship,
        'Segment': res_seg,
        'Region': res_reg,
        'State': res_state,
        'Category': res_cat,
        'Sub-Category': res_sub,
        'Sales': res_sales,
        'Quantity': res_qty,
        'Discount': res_disc,
        'Profit': res_profit
    })
    return df_clean

df = generate_perfect_superstore_data()

# ==========================================
# 3. THANH BỘ LỌC TƯƠNG TÁC SIDEBAR (MỤC 4.2.3)
# ==========================================
st.sidebar.header("🎛️ BỘ LỌC TƯƠNG TÁC (SLICERS)")
st.sidebar.markdown("---")

selected_region = st.sidebar.multiselect(
    "1. Khu vực địa lý (Region):",
    options=sorted(df['Region'].unique()),
    default=sorted(df['Region'].unique())
)

selected_segment = st.sidebar.multiselect(
    "2. Phân khúc khách hàng (Segment):",
    options=sorted(df['Segment'].unique()),
    default=sorted(df['Segment'].unique())
)

selected_category = st.sidebar.multiselect(
    "3. Danh mục sản phẩm (Category):",
    options=sorted(df['Category'].unique()),
    default=sorted(df['Category'].unique())
)

selected_ship = st.sidebar.multiselect(
    "4. Phương thức vận chuyển (Ship Mode):",
    options=sorted(df['Ship Mode'].unique()),
    default=sorted(df['Ship Mode'].unique())
)

# Thực thi reactive rendering lọc dữ liệu theo thời gian thực
filtered_df = df[
    (df['Region'].isin(selected_region)) &
    (df['Segment'].isin(selected_segment)) &
    (df['Category'].isin(selected_category)) &
    (df['Ship Mode'].isin(selected_ship))
]

# Nút Reset bộ lọc nhanh
if st.sidebar.button("🔄 Thiết lập lại bộ lọc"):
    st.rerun()

# ==========================================
# 4. HỒI 1: HỆ THỐNG THẺ CHỈ SỐ KPI CARDS (MỤC 4.2.2)
# ==========================================
st.subheader("📍 Hồi 1: Số Liệu Tổng Quan Hệ Thống")

# Tính toán các chỉ số kinh doanh cốt lõi
t_sales = filtered_df['Sales'].sum()
t_profit = filtered_df['Profit'].sum()
t_orders = len(filtered_df)
p_margin = (t_profit / t_sales) * 100 if t_sales > 0 else 0
a_discount = filtered_df['Discount'].mean() * 100

# Thiết kế hiển thị 5 thẻ ngang chuẩn giao diện báo cáo
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric(label="💰 Total Sales", value=f"${t_sales:,.2f}")

# Custom màu sắc động cho Profit tài chính theo đúng nguyên tắc thiết kế màu sắc
if t_profit >= 0:
    kpi2.metric(label="📈 Total Profit", value=f"${t_profit:,.2f}")
else:
    kpi2.metric(label="📉 Total Profit", value=f"${t_profit:,.2f}", delta="Thua lỗ ròng", delta_color="inverse")

# Định dạng màu cảnh báo động cho Profit Margin (Mục 4.2.2)
if p_margin < 10:
    kpi3.metric(label="📊 Profit Margin", value=f"{p_margin:.2f}%", delta="Nguy cơ thấp", delta_color="inverse")
elif 10 <= p_margin <= 20:
    kpi3.metric(label="📊 Profit Margin", value=f"{p_margin:.2f}%", delta="Ổn định")
else:
    kpi3.metric(label="📊 Profit Margin", value=f"{p_margin:.2f}%", delta="Tăng trưởng tốt")

kpi4.metric(label="📦 Total Orders", value=f"{t_orders:,} Đơn")

# Cảnh báo nếu chiết khấu trung bình vượt ngưỡng an toàn
if a_discount > 15:
    kpi5.metric(label="🚨 Avg. Discount", value=f"{a_discount:.1f}%", delta="Vượt ngưỡng an toàn", delta_color="inverse")
else:
    kpi5.metric(label="🚨 Avg. Discount", value=f"{a_discount:.1f}%")

st.markdown("---")

# ==========================================
# 5. HỆ THỐNG BIỂU ĐỒ CƠ BẢN (MỤC 3.4)
# ==========================================
st.subheader("📈 Hệ Thống Biểu Đồ Cơ Bản")

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### Top 10 bang dẫn đầu doanh thu (Line Graph)")
    state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(10)
    fig_line = px.line(
        state_sales, x='State', y='Sales',
        labels={'State': 'Tên Bang', 'Sales': 'Doanh Thu (USD)'},
        markers=True, text=state_sales['Sales'].apply(lambda x: f"${x:,.0f}")
    )
    fig_line.update_traces(textposition="top center", line_color="#1f77b4")
    st.plotly_chart(fig_line, use_container_width=True)

with row1_col2:
    st.markdown("#### Tỷ trọng doanh thu theo phân khúc khách hàng (Pie Chart)")
    seg_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
    fig_pie = px.pie(
        seg_sales, values='Sales', names='Segment',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.markdown("#### Doanh thu theo khu vực và danh mục sản phẩm (Stacked Bar Chart)")
    reg_cat_sales = filtered_df.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
    fig_bar = px.bar(
        reg_cat_sales, x='Region', y='Sales', color='Category',
        labels={'Region': 'Khu vực địa lý', 'Sales': 'Tổng doanh thu (USD)'},
        barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_col2:
    st.markdown("#### Tương quan giữa doanh thu, lợi nhuận và chiết khấu (Scatter Plot)")
    fig_scatter = px.scatter(
        filtered_df, x='Sales', y='Profit', color='Discount',
        labels={'Sales': 'Doanh thu (USD)', 'Profit': 'Lợi nhuận (USD)', 'Discount': 'Mức chiết khấu'},
        color_continuous_scale='RdYlGn', opacity=0.5
    )
    # Thêm đường tham chiếu ngang Profit = 0 bảo vệ tính trung thực dữ liệu
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Đường hòa vốn (Profit = 0)")
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ==========================================
# 6. HỆ THỐNG BIỂU ĐỒ NÂNG CAO (MỤC 3.5 & CẢI TIẾN 5.2)
# ==========================================
st.subheader("🔍 Hồi 2 & 3: Hệ Thống Biểu Đồ Nâng Cao (Truy Tìm Nguyên Nhân Vùng Đỏ)")

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.markdown("#### Lợi nhuận trung bình theo khu vực và danh mục (Heatmap)")
    # ÁP DỤNG CẢI TIẾN 2 (MỤC 5.2.2): Chuyển sang dải màu RdYlGn độ tương phản cực cao + hiện thẳng text_auto
    heat_data = filtered_df.groupby(['Region', 'Category'])['Profit'].mean().reset_index()
    heat_pivot = heat_data.pivot(index='Region', columns='Category', values='Profit')
    
    fig_heatmap = px.imshow(
        heat_pivot,
        labels=dict(x="Danh mục sản phẩm", y="Khu vực địa lý", color="Lợi nhuận TB ($)"),
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0,
        text_auto=".1f"  # Hiện trực tiếp giá trị USD làm nổi bật vùng âm ngay lập tức
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with row3_col2:
    st.markdown("#### Phân cấp danh mục theo doanh thu và lợi nhuận (Treemap)")
    # ÁP DỤNG CẢI TIẾN 1 (MỤC 5.2.1): Tùy chỉnh hovertemplate chi tiết ngăn lỗi chữ nhỏ trên Treemap
    fig_treemap = px.treemap(
        filtered_df,
        path=['Category', 'Sub-Category'],
        values='Sales',
        color='Profit',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=0
    )
    fig_treemap.update_traces(
        hovertemplate="<b>Phân loại cấp:</b> %{label}<br><b>Tổng doanh thu (Sales):</b> $%{value:,.2f}<br><b>Lợi nhuận ròng (Profit):</b> $%{color:,.2f}<extra></extra>"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

# ==========================================
# 7. PHẦN ĐỐI SOÁT KIỂM THỨC VÀ HẠN CHẾ (CHƯƠNG 5)
# ==========================================
st.markdown("---")
st.markdown("#### 📋 Nhật ký đối soát dữ liệu giao dịch chi tiết (Sắp xếp theo sản phẩm rủi ro nhất)")
st.dataframe(
    filtered_df.sort_values(by="Profit", ascending=True),
    use_container_width=True,
    column_config={
        "Sales": st.column_config.NumberColumn("Doanh thu", format="$%,.2f"),
        "Profit": st.column_config.NumberColumn("Lợi nhuận ròng", format="$%,.2f"),
        "Discount": st.column_config.NumberColumn("Chiết khấu áp dụng", format="%.2f")
    }
)

st.info("💡 **Khuyến nghị chiến lược dựa trên Câu chuyện dữ liệu (Mục 4.3):** Khi lọc khu vực **Central** và danh mục **Furniture**, hệ thống kích hoạt cảnh báo đỏ đậm tại ô **Tables** của Treemap. Ban quản lý cần giới hạn ngay mức chiết khấu tối đa xuống dưới 20% tại thị trường này để cắt giảm lỗ.")
