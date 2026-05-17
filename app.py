import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CẤU HÌNH GIAO DIỆN HIỆN ĐẠI (UI/UX CHUẨN BÁO CÁO)
# ==============================================================================
st.set_page_config(
    page_title="Superstore Sales & Profit Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tùy chỉnh CSS giao diện: Tăng độ tương phản, bo góc, tạo đổ bóng nhẹ cho các thẻ KPI
st.markdown("""
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
    h1 {color: #1E3A8A; font-weight: 700; margin-bottom: 0.5rem;}
    h2, h3 {color: #2C3E50; font-weight: 600;}
    .kpi-card {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        text-align: center;
        margin-bottom: 10px;
    }
    .kpi-title { font-size: 13px; color: #6B7280; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-value { font-size: 24px; font-weight: 700; margin-top: 5px; }
    /* Định dạng thanh Tab điều hướng hiện đại */
    .stTabs [data-baseweb="tab-list"] { gap: 16px; }
    .stTabs [data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
        padding: 10px 20px;
        border-radius: 4px 4px 0px 0px;
        color: #4B5563;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1E3A8A;
        border-bottom-color: #1E3A8A;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. ĐỌC VÀ TIỀN XỬ LÝ DỮ LIỆU THỰC TẾ
# ==============================================================================
@st.cache_data
def load_data():
    try:
        # Đọc trực tiếp từ tập dữ liệu mẫu của nhóm
        df = pd.read_csv("SampleSuperstore.csv")
    except FileNotFoundError:
        st.error("Không tìm thấy file 'SampleSuperstore.csv'. Hãy đảm bảo file nằm cùng thư mục với file app.py này!")
        st.stop()
        
    # Chuẩn hóa khoảng trắng cho dữ liệu dạng chuỗi như báo cáo mô tả
    string_cols = ['Ship Mode', 'Segment', 'Region', 'Category', 'Sub-Category', 'State']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].str.strip()
            
    return df

df = load_data()

# ==============================================================================
# 3. THANH SIDEBAR - BỘ LỌC TƯƠNG TÁC (SLICERS)
# ==============================================================================
st.sidebar.header("Bộ Lọc Hệ Thống")

# Khởi tạo các bộ lọc đa chọn (Mặc định chọn tất cả)
region_sel = st.sidebar.multiselect("Khu vực (Region)", options=sorted(df['Region'].unique()), default=df['Region'].unique())
segment_sel = st.sidebar.multiselect("Phân khúc (Segment)", options=sorted(df['Segment'].unique()), default=df['Segment'].unique())
category_sel = st.sidebar.multiselect("Danh mục (Category)", options=sorted(df['Category'].unique()), default=df['Category'].unique())
ship_sel = st.sidebar.multiselect("Phương thức vận chuyển (Ship Mode)", options=sorted(df['Ship Mode'].unique()), default=df['Ship Mode'].unique())

# Áp dụng bộ lọc động vào dữ liệu
df_filtered = df[
    (df['Region'].isin(region_sel)) &
    (df['Segment'].isin(segment_sel)) &
    (df['Category'].isin(category_sel)) &
    (df['Ship Mode'].isin(ship_sel))
]

# Tính toán các chỉ số cốt lõi (KPIs)
total_sales = df_filtered['Sales'].sum() if not df_filtered.empty else 0
total_profit = df_filtered['Profit'].sum() if not df_filtered.empty else 0
profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
total_orders = len(df_filtered)
avg_discount = (df_filtered['Discount'].mean() * 100) if not df_filtered.empty else 0

# Tự động chuyển đổi màu sắc biên lợi nhuận để cảnh báo rủi ro
if profit_margin < 10:
    margin_color = "#DC2626"   # Đỏ rủi ro cao
elif profit_margin <= 20:
    margin_color = "#D97706"   # Vàng cảnh báo trung bình
else:
    margin_color = "#16A34A"   # Xanh lá an toàn

# ==============================================================================
# 4. VÙNG HIỂN THỊ CHÍNH (MAIN VISUALIZATION AREA)
# ==============================================================================
st.title("📊 Hệ Thống Phân Tích & Trực Quan Hóa Dữ Liệu Bán Hàng Superstore")
st.caption("Đồ án môn học Trực quan hóa dữ liệu — Nhóm 14 — Lớp D22CNTT06 — GVHD: TS. Lê Thị Thùy Trang")

# ---- TẦNG 1: HỆ THỐNG THỂ KPI HIỆN ĐẠI (Đồng bộ thông tin tổng quan) ----
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Tổng Doanh Thu</div><div class='kpi-value' style='color:#1E3A8A;'>${total_sales:,.2f}</div></div>", unsafe_allow_html=True)

with kpi2:
    profit_text_color = "#DC2626" if total_profit < 0 else "#1E3A8A"
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Tổng Lợi Nhuận</div><div class='kpi-value' style='color:{profit_text_color};'>${total_profit:,.2f}</div></div>", unsafe_allow_html=True)

with kpi3:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Biên Lợi Nhuận</div><div class='kpi-value' style='color:{margin_color};'>{profit_margin:.2f}%</div></div>", unsafe_allow_html=True)

with kpi4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Tổng Số Đơn Hàng</div><div class='kpi-value' style='color:#1E3A8A;'>{total_orders:,}</div></div>", unsafe_allow_html=True)

with kpi5:
    disc_delta_color = "#DC2626" if avg_discount > 30 else "#16A34A"
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Chiết Khấu Trung Bình</div><div class='kpi-value' style='color:{disc_delta_color};'>{avg_discount:.2f}%</div></div>", unsafe_allow_html=True)

st.write("")

# ---- TẦNG 2: PHÂN TÁCH BỐ CỤC BẰNG TABS ĐỂ TRÁNH RỐI MẮT KHI CHÚNG TA CHỤP ẢNH ----
tab_basic, tab_advanced = st.tabs(["📈 Phân Tích Khám Phá Cơ Bản", "🎯 Phân Tích Chuyên Sâu Nâng Cao"])

# ==============================================================================
# TAB 1: HỆ THỐNG BIỂU ĐỒ CƠ BẢN
# ==============================================================================
with tab_basic:
    st.markdown("### Phân Tích Xu Hướng Và Tỷ Trọng Doanh Thu")
    col1, col2 = st.columns(2)
    
    with col1:
        # Biểu đồ 1: Line Graph - Top 10 bang có doanh thu cao nhất
        state_sales = df_filtered.groupby('State')['Sales'].sum().reset_index()
        top10_states = state_sales.sort_values(by='Sales', ascending=False).head(10)
        
        fig_line = px.line(
            top10_states, x='State', y='Sales', 
            text=top10_states['Sales'].map(lambda x: f"${x:,.0f}"),
            title="Top 10 Bang Dẫn Đầu Về Doanh Thu Toàn Hệ Thống",
            labels={'Sales': 'Doanh Thu (USD)', 'State': 'Bang'},
            markers=True
        )
        fig_line.update_traces(textposition="top center", line_color="#1FA2FF")
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=True, gridcolor="#E5E7EB"))
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Biểu đồ 2: Stacked Bar Chart - Doanh thu theo khu vực và danh mục sản phẩm
        region_cat_sales = df_filtered.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
        
        fig_stacked = px.bar(
            region_cat_sales, x='Region', y='Sales', color='Category',
            title="Phân Phối Doanh Thu Theo Khu Vực Địa Lý Và Danh Mục Sản Phẩm",
            labels={'Sales': 'Doanh Thu (USD)', 'Region': 'Khu Vực'},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_stacked.update_layout(plot_bgcolor="rgba(0,0,0,0)", barmode='stack')
        st.plotly_chart(fig_stacked, use_container_width=True)

    with col2:
        # Biểu đồ 3: Pie Chart - Tỷ trọng doanh thu theo phân khúc khách hàng
        segment_sales = df_filtered.groupby('Segment')['Sales'].sum().reset_index()
        
        fig_pie = px.pie(
            segment_sales, values='Sales', names='Segment', hole=0.35,
            title="Tỷ Trọng Đóng Góp Doanh Thu Của Các Phân Khúc Khách Hàng",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pie.update_traces(textinfo='percent+label', pull=[0.02, 0, 0])
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Biểu đồ 4: Scatter Plot - Mối liên hệ giữa Doanh thu, Lợi nhuận và Chiết khấu
        fig_scatter = px.scatter(
            df_filtered, x='Sales', y='Profit', color='Discount', opacity=0.6,
            title="Tương Quan Phân Kỳ Giữa Doanh Thu, Lợi Nhuận Và Tỷ Lệ Chiết Khấu",
            labels={'Sales': 'Doanh Thu (USD)', 'Profit': 'Lợi Nhuận (USD)', 'Discount': 'Mức Chiết Khấu'},
            color_continuous_scale=px.colors.sequential.RdBu_r
        )
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="#EF4444", annotation_text="Điểm hòa vốn")
        st.plotly_chart(fig_scatter, use_container_width=True)

# ==============================================================================
# TAB 2: HỆ THỐNG BIỂU ĐỒ NÂNG CAO (THÊM BỘ LỌC CHẾ ĐỘ XEM ĐỂ TỐI ƯU KHÔNG GIAN)
# ==============================================================================
with tab_advanced:
    st.markdown("### Định Vị Rủi Ro Và Phân Cấp Lợi Nhuận")
    
    # Bộ lọc radio cho phép mở rộng không gian hiển thị cho biểu đồ lớn
    view_option = st.radio(
        "**Tùy chọn hiển thị biểu đồ nâng cao:**",
        options=["Xem Heatmap (Mở rộng toàn màn hình)", "Xem Treemap (Mở rộng toàn màn hình)", "Xem song song cả hai biểu đồ"],
        horizontal=True
    )
    
    st.write("---")
    
    if not df_filtered.empty:
        # Khởi tạo các cấu trúc đồ họa nâng cao
        # 1. Heatmap lợi nhuận trung bình (Cải tiến dải màu RdYlGn và nhãn text tự động)
        pivot_heatmap = df_filtered.pivot_table(index='Region', columns='Category', values='Profit', aggfunc='mean').round(2)
        fig_heatmap = px.imshow(
            pivot_heatmap,
            text_auto='.2f', 
            color_continuous_scale='RdYlGn',  # Thang màu Đỏ - Vàng - Xanh chuẩn cam kết báo cáo
            title="Heatmap: Chỉ Số Lợi Nhuận Trung Bình Theo Vùng Và Ngành Hàng",
            labels=dict(x="Danh Mục Sản Phẩm", y="Khu Vực", color="Lợi Nhuận TB ($)")
        )
        
        # 2. Treemap cấu trúc phân cấp (Cải tiến Hover Tooltip chi tiết phục vụ Data Storytelling)
        df_tree = df_filtered.groupby(['Category', 'Sub-Category']).agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        fig_treemap = px.treemap(
            df_tree, 
            path=['Category', 'Sub-Category'], 
            values='Sales',
            color='Profit',
            color_continuous_scale='RdYlGn',
            title="Treemap: Cấu Trúc Phân Cấp Sản Phẩm Theo Quy Mô Doanh Thu & Lợi Nhuận"
        )
        fig_treemap.update_traces(
            hovertemplate="<b>Danh mục:</b> %{label}<br><b>Tổng Doanh Thu (Diện tích):</b> $%{value:,.2f}<br><b>Tổng Lợi Nhuận (Màu sắc):</b> $%{color:,.2f}<extra></extra>"
        )
        
        # Điều phối bố cục hiển thị dựa trên bộ lọc đã chọn
        if view_option == "Xem Heatmap (Mở rộng toàn màn hình)":
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        elif view_option == "Xem Treemap (Mở rộng toàn màn hình)":
            st.plotly_chart(fig_treemap, use_container_width=True)
            
        else: # Chế độ hiển thị song song
            col3, col4 = st.columns(2)
            with col3:
                st.plotly_chart(fig_heatmap, use_container_width=True)
            with col4:
                st.plotly_chart(fig_treemap, use_container_width=True)
                
    else:
        st.info("Không có dữ liệu phù hợp với bộ lọc hiện tại để hiển thị phân tích nâng cao.")
