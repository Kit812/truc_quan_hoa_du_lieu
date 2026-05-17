import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN HỆ THỐNG (CHƯƠNG 4)
# ==========================================
st.set_page_config(
    page_title="Superstore BI Platform",
    page_icon="🏢",
    layout="wide"
)

# Thanh tiêu đề cố định ở đầu trang theo chuẩn đồ án
st.title("🏢 HỆ THỐNG PHÂN TÍCH HIỆU SUẤT THƯƠNG MẠI")
st.markdown("### 📊 Superstore Executive Business Intelligence Platform")
st.caption("Đồ án Trực quan hóa dữ liệu | Thực hiện bởi: Nhóm 14 - Lớp D22CNTT06")
st.markdown("---")

# ==========================================
# 2. ĐỌC VÀ TIỀN XỬ LÝ DỮ LIỆU THỰC TẾ (CHƯƠNG 3)
# ==========================================
@st.cache_data
def load_actual_superstore_data():
    """
    Hàm nạp file dữ liệu thật từ GitHub và tự động thực hiện chuẩn hóa tên cột
    theo đúng quy trình tiền xử lý được mô tả trong đồ án (Mục 3.2.1).
    """
    try:
        # Đọc file dữ liệu thật nằm cùng thư mục với app.py
        data = pd.read_csv("SampleSuperstore.csv")
        
        # Tiền xử lý: Chuẩn hóa tên cột, loại bỏ khoảng trắng thừa (Bảng 3.3)
        data.columns = data.columns.str.strip()
        
        return data
    except FileNotFoundError:
        st.error("🚨 **Lỗi hệ thống:** Không tìm thấy file 'SampleSuperstore.csv' trong kho lưu trữ GitHub của bạn. Vui lòng tải file dữ liệu lên ngang hàng với file app.py.")
        st.stop()

df = load_actual_superstore_data()

# ==========================================
# 3. TRUNG TÂM ĐIỀU KHIỂN & BỘ LỌC TOÀN CỤC (SIDEBAR)
# ==========================================
st.sidebar.markdown("### 🎛️ BỘ LỌC DỮ LIỆU TOÀN CỤC")
st.sidebar.caption("Áp dụng đồng bộ lên số liệu của cả 3 phân hệ phân tích.")
st.sidebar.markdown("---")

# Bộ lọc dữ liệu kinh doanh đa lựa chọn (Mục 4.2.3)
selected_region = st.sidebar.multiselect("🌍 Khu vực (Region):", options=sorted(df['Region'].unique()), default=sorted(df['Region'].unique()))
selected_segment = st.sidebar.multiselect("👥 Phân khúc (Segment):", options=sorted(df['Segment'].unique()), default=sorted(df['Segment'].unique()))
selected_category = st.sidebar.multiselect("📦 Danh mục sản phẩm (Category):", options=sorted(df['Category'].unique()), default=sorted(df['Category'].unique()))
selected_ship = st.sidebar.multiselect("🚚 Vận chuyển (Ship Mode):", options=sorted(df['Ship Mode'].unique()), default=sorted(df['Ship Mode'].unique()))

# Thực thi lọc dữ liệu động theo thời gian thực
filtered_df = df[
    (df['Region'].isin(selected_region)) & (df['Segment'].isin(selected_segment)) &
    (df['Category'].isin(selected_category)) & (df['Ship Mode'].isin(selected_ship))
]

st.sidebar.markdown("---")
if st.sidebar.button("🔄 Khởi động lại bộ lọc"):
    st.rerun()

# ==========================================
# 4. HỆ THỐNG PHÂN TÁCH PHÂN HỆ BIẾN ĐỘNG (TABS)
# ==========================================
tab_kpi, tab_diagnostic, tab_audit = st.tabs([
    "📈 Phân Hệ 1: Hiệu Suất Tổng Quan", 
    "🔍 Phân Hệ 2: Chẩn Đoán & Phát Hiện Rủi Ro Lỗ/Lãi", 
    "📋 Phân Hệ 3: Đối Soát Dữ Liệu Giao Dịch Chi Tiết"
])

# ------------------------------------------
# TAB 1: HIỆU SUẤT TỔNG QUAN (DESCRIPTIVE INSIGHTS)
# ------------------------------------------
with tab_kpi:
    st.markdown("#### 📌 Báo cáo Sức khỏe Doanh nghiệp (Thống kê Mô tả)")
    
    # Tính toán các thẻ chỉ số cốt lõi (Mục 4.2.2)
    t_sales = filtered_df['Sales'].sum()
    t_profit = filtered_df['Profit'].sum()
    p_margin = (t_profit / t_sales) * 100 if t_sales > 0 else 0
    t_orders = len(filtered_df)
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(label="💰 Tổng doanh thu", value=f"${t_sales:,.2f}")
    
    if t_profit >= 0:
        k2.metric(label="📈 Lợi nhuận ròng", value=f"${t_profit:,.2f}")
    else:
        k2.metric(label="📉 Lợi nhuận ròng", value=f"${t_profit:,.2f}", delta="Thua lỗ ròng", delta_color="inverse")
        
    k3.metric(label="📊 Biên lợi nhuận (Margin)", value=f"{p_margin:.2f}%")
    k4.metric(label="📦 Tổng số đơn hàng", value=f"{t_orders:,} Đơn")
    
    st.markdown("---")
    
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        st.markdown("##### Phân phối Doanh thu theo Khu vực địa lý & Danh mục (Stacked Bar Chart)")
        reg_cat_sales = filtered_df.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
        fig_bar = px.bar(reg_cat_sales, x='Region', y='Sales', color='Category', barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col1_2:
        st.markdown("##### Tỉ trọng đóng góp Doanh thu theo Phân khúc Khách hàng (Pie Chart)")
        seg_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
        fig_pie = px.pie(seg_sales, values='Sales', names='Segment', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("##### Top 10 Thị trường cấp Bang dẫn đầu Doanh thu (Line Graph)")
    state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(10)
    fig_line = px.line(state_sales, x='State', y='Sales', labels={'Sales': 'Doanh thu (USD)', 'State': 'Tên Bang'}, markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------
# TAB 2: CHẨN ĐOÁN & PHÁT HIỆN RỦI RO (BỘ LỌC ĐẶT NỘI BỘ TRONG TAB)
# ------------------------------------------
with tab_diagnostic:
    st.markdown("#### 📌 Phân tích chẩn đoán chuyên sâu nguyên nhân thua lỗ")
    
    # Bộ lọc cô lập nội bộ phân hệ góc nhìn diện rộng
    col_filter_1, col_filter_2 = st.columns([1, 2])
    with col_filter_1:
        view_mode = st.selectbox(
            "🖥️ **Bộ lọc cấu trúc không gian hiển thị (Phân hệ 2):**",
            options=[
                "📱 Hiển thị thu gọn (Xem song song tất cả)", 
                "📈 Phóng to Ma trận nhiệt (Heatmap)", 
                "🌳 Phóng to Biểu đồ cây phân cấp (Treemap)",
                "🎯 Phóng to Mô hình phân tán Chiết khấu (Scatter)"
            ],
            index=0
        )
    st.markdown("---")
    
    # Khởi tạo các biểu đồ phân tích nâng cao (Mục 3.5)
    # 1. Định nghĩa Heatmap (Áp dụng cải tiến hiển thị số tiền trực tiếp text_auto - Mục 5.2.2)
    heat_data = filtered_df.groupby(['Region', 'Category'])['Profit'].mean().reset_index()
    heat_pivot = heat_data.pivot(index='Region', columns='Category', values='Profit').fillna(0)
    fig_heatmap = px.imshow(heat_pivot, color_continuous_scale='RdYlGn', color_continuous_midpoint=0, text_auto=".1f")
    
    # 2. Định nghĩa Treemap (Áp dụng cải tiến hovertemplate chi tiết - Mục 5.2.1)
    fig_treemap = px.treemap(filtered_df, path=['Category', 'Sub-Category'], values='Sales', color='Profit', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
    fig_treemap.update_traces(hovertemplate="<b>Phân loại:</b> %{label}<br><b>Doanh thu:</b> $%{value:,.2f}<br><b>Lợi nhuận:</b> $%{color:,.2f}<extra></extra>")
    
    # 3. Định nghĩa Scatter Plot (Mục 3.4.4)
    fig_scatter = px.scatter(filtered_df, x='Sales', y='Profit', color='Discount', color_continuous_scale='RdYlGn', opacity=0.5)
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black")

    # Điều phối luồng hiển thị diện rộng theo bộ lọc góc nhìn
    if view_mode == "📱 Hiển thị thu gọn (Xem song song tất cả)":
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.markdown("##### Ma trận nhiệt (Heatmap): Hiệu suất sinh lời trung bình (Region vs Category)")
            fig_heatmap.update_layout(height=380)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        with col2_2:
            st.markdown("##### Biểu đồ phân cấp Cây (Treemap): Cơ cấu doanh thu và lợi nhuận")
            fig_treemap.update_layout(height=380)
            st.plotly_chart(fig_treemap, use_container_width=True)
            
        st.markdown("---")
        st.markdown("##### Mô hình phân tán: Tác động biên của mức Chiết khấu đến biên Lợi nhuận")
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    elif view_mode == "📈 Phóng to Ma trận nhiệt (Heatmap)":
        st.markdown("##### 📐 [CHẾ ĐỘ PHÓNG TO RỘNG MÀN HÌNH] Ma trận nhiệt (Heatmap): Hiệu suất sinh lời trung bình")
        fig_heatmap.update_layout(height=650) 
        st.plotly_chart(fig_heatmap, use_container_width=True)
        st.info("💡 **Gợi ý phân tích dữ liệu thật:** Hãy chú ý các ô mang màu sắc đỏ/cam đậm. Đó chính là các vùng thị trường và danh mục hàng hóa đang bị bào mòn dòng tiền nặng nhất.")
        
    elif view_mode == "🌳 Phóng to Biểu đồ cây phân cấp (Treemap)":
        st.markdown("##### 📐 [CHẾ ĐỘ PHÓNG TO RỘNG MÀN HÌNH] Biểu đồ phân cấp Cây (Treemap): Phân tích cơ cấu doanh thu & rủi ro")
        fig_treemap.update_layout(height=650)
        st.plotly_chart(fig_treemap, use_container_width=True)
        st.info("💡 **Gợi ý phân tích dữ liệu thật:** Khối hộp nào có diện tích lớn thể hiện quy mô doanh thu cao. Nếu khối hộp đó mang sắc đỏ rực, ban quản lý cần rà soát lại ngay chính sách giá lẻ.")
        
    elif view_mode == "🎯 Phóng to Mô hình phân tán Chiết khấu (Scatter)":
        st.markdown("##### 📐 [CHẾ ĐỘ PHÓNG TO RỘNG MÀN HÌNH] Mô hình phân tán tương quan Sales vs Profit")
        fig_scatter.update_layout(height=650)
        st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------
# TAB 3: ĐỐI SOÁT DỮ LIỆU GIAO DỊCH CHI TIẾT (DATA AUDIT LOG)
# ------------------------------------------
with tab_audit:
    st.markdown("#### 📌 Nhật ký đối soát dữ liệu giao dịch chi tiết (Data Audit Log)")
    st.caption("Bảng dữ liệu thực tế trích xuất trực tiếp từ file đồ án, được tự động sắp xếp theo thứ tự Lợi nhuận từ thấp nhất đến cao nhất phục vụ rà soát lỗ.")
    
    st.dataframe(
        filtered_df.sort_values(by="Profit", ascending=True),
        use_container_width=True,
        column_config={
            "Sales": st.column_config.NumberColumn("Doanh thu (USD)", format="$%,.2f"),
            "Profit": st.column_config.NumberColumn("Lợi nhuận ròng (USD)", format="$%,.2f"),
            "Discount": st.column_config.NumberColumn("Mức chiết khấu", format="%.2f")
        }
    )
    
    st.markdown("---")
    st.info("💡 **Khuyến nghị chiến lược quản trị (Mục 5.5):** Dựa vào kết quả phân tích chẩn đoán đa chiều tại Phân hệ 2, chuỗi siêu thị cần kiểm soát chặt chẽ biên độ khuyến mãi, đặc biệt thiết lập trần chiết khấu tối đa không vượt quá 20% cho các nhóm hàng rủi ro cao.")
