import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN HỆ THỐNG
# ==========================================
st.set_page_config(
    page_title="Superstore BI Platform",
    page_icon="🏢",
    layout="wide"
)

# Thanh tiêu đề cố định ở đầu trang
st.title("🏢 HỆ THỐNG PHÂN TÍCH HIỆU SUẤT THƯƠNG MẠI")
st.markdown("### 📊 Superstore Executive Business Intelligence Platform")
st.caption("Đồ án Trực quan hóa dữ liệu | Thực hiện bởi: Nhóm 14 - Lớp D22CNTT06")
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
    return pd.DataFrame({
        'Ship Mode': res_ship, 'Segment': res_seg, 'Region': res_reg,
        'State': res_state, 'Category': res_cat, 'Sub-Category': res_sub,
        'Sales': res_sales, 'Quantity': res_qty, 'Discount': res_disc, 'Profit': res_profit
    })

df = generate_perfect_superstore_data()

# ==========================================
# 3. TRUNG TÂM ĐIỀU KHIỂN & BỘ LỌC TƯƠNG TÁC (SIDEBAR CHI SẺ CHUNG)
# ==========================================
st.sidebar.markdown("### 🎛️ BỘ LỌC DỮ LIỆU TOÀN CỤC")
st.sidebar.caption("Các bộ lọc dưới đây sẽ áp dụng đồng bộ lên tất cả các phân hệ phân tích.")
st.sidebar.markdown("---")

selected_region = st.sidebar.multiselect("🌍 Khu vực (Region):", options=sorted(df['Region'].unique()), default=sorted(df['Region'].unique()))
selected_segment = st.sidebar.multiselect("👥 Phân khúc (Segment):", options=sorted(df['Segment'].unique()), default=sorted(df['Segment'].unique()))
selected_category = st.sidebar.multiselect("📦 Danh mục sản phẩm (Category):", options=sorted(df['Category'].unique()), default=sorted(df['Category'].unique()))
selected_ship = st.sidebar.multiselect("🚚 Vận chuyển (Ship Mode):", options=sorted(df['Ship Mode'].unique()), default=sorted(df['Ship Mode'].unique()))

# Áp dụng bộ lọc chung cho biến filtered_df
filtered_df = df[
    (df['Region'].isin(selected_region)) & (df['Segment'].isin(selected_segment)) &
    (df['Category'].isin(selected_category)) & (df['Ship Mode'].isin(selected_ship))
]

if st.sidebar.button("🔄 Khởi động lại bộ lọc"):
    st.rerun()

# ==========================================
# 4. HỆ THỐNG PHÂN PHÁP TAB CHUYÊN NGHIỆP
# ==========================================
# Chia Dashboard làm 3 Tab nội dung rõ ràng
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
    
    # Khu vực KPI Cards thu gọn
    t_sales = filtered_df['Sales'].sum()
    t_profit = filtered_df['Profit'].sum()
    p_margin = (t_profit / t_sales) * 100 if t_sales > 0 else 0
    t_orders = len(filtered_df)
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(label="💰 Tổng doanh thu", value=f"${t_sales:,.2f}")
    if t_profit >= 0:
        k2.metric(label="📈 Lợi nhuận ròng", value=f"${t_profit:,.2f}")
    else:
        k2.metric(label="📉 Lợi nhuận ròng", value=f"${t_profit:,.2f}", delta="Thua lỗ", delta_color="inverse")
    k3.metric(label="📊 Biên lợi nhuận (Margin)", value=f"{p_margin:.2f}%")
    k4.metric(label="📦 Tổng số đơn hàng", value=f"{t_orders:,} Đơn")
    
    st.markdown("---")
    
    # Chỉ để 3 biểu đồ cơ bản nhất ở trang này để giữ không gian thoáng
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        st.markdown("##### Phân phối Doanh thu theo Khu vực địa lý & Danh mục")
        reg_cat_sales = filtered_df.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
        fig_bar = px.bar(reg_cat_sales, x='Region', y='Sales', color='Category', barmode='stack', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col1_2:
        st.markdown("##### Tỉ trọng đóng góp Doanh thu theo Phân khúc Khách hàng")
        seg_sales = filtered_df.groupby('Segment')['Sales'].sum().reset_index()
        fig_pie = px.pie(seg_sales, values='Sales', names='Segment', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("##### Top 10 Thị trường cấp Bang dẫn đầu Doanh thu")
    state_sales = filtered_df.groupby('State')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False).head(10)
    fig_line = px.line(state_sales, x='State', y='Sales', labels={'Sales': 'Doanh thu (USD)'}, markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------
# TAB 2: CHẨN ĐOÁN & PHÁT HIỆN RỦI RO LỖ/LÃI (DIAGNOSTIC INSIGHTS)
# ------------------------------------------
with tab_diagnostic:
    st.markdown("#### 📌 Phân tích chẩn đoán chuyên sâu nguyên nhân thua lỗ")
    st.caption("Trang phân tích này tập trung ứng dụng các biểu đồ cấu trúc nâng cao để dò tìm các điểm nóng (Hotspots) ảnh hưởng tiêu cực đến dòng tiền.")
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        st.markdown("##### Ma trận nhiệt (Heatmap): Hiệu suất sinh lời trung bình (Region vs Category)")
        heat_data = filtered_df.groupby(['Region', 'Category'])['Profit'].mean().reset_index()
        heat_pivot = heat_data.pivot(index='Region', columns='Category', values='Profit')
        fig_heatmap = px.imshow(heat_pivot, color_continuous_scale='RdYlGn', color_continuous_midpoint=0, text_auto=".1f")
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    with col2_2:
        st.markdown("##### Biểu đồ phân cấp Cây (Treemap): Cơ cấu rủi ro theo Danh mục phụ")
        fig_treemap = px.treemap(filtered_df, path=['Category', 'Sub-Category'], values='Sales', color='Profit', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
        fig_treemap.update_traces(hovertemplate="<b>Phân loại:</b> %{label}<br><b>Doanh thu:</b> $%{value:,.2f}<br><b>Lợi nhuận:</b> $%{color:,.2f}<extra></extra>")
        st.plotly_chart(fig_treemap, use_container_width=True)
        
    st.markdown("---")
    st.markdown("##### Mô hình phân tán: Tác động biên của chính sách Chiết khấu (Discount) đến Lợi nhuận (Profit)")
    fig_scatter = px.scatter(filtered_df, x='Sales', y='Profit', color='Discount', color_continuous_scale='RdYlGn', opacity=0.5)
    fig_scatter.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Đường hòa vốn (Profit = 0)")
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------
# TAB 3: ĐỐI SOÁT DỮ LIỆU GIAO DỊCH CHI TIẾT (DATA AUDIT LOG)
# ------------------------------------------
with tab_audit:
    st.markdown("#### 📌 Nhật ký đối soát dữ liệu giao dịch chi tiết (Data Audit Log)")
    st.caption("Bảng dữ liệu thô đã qua tiền xử lý, sắp xếp tự động từ các giao dịch rủi ro/gây lỗ nặng nhất lên đầu để phục vụ việc truy vết đơn hàng.")
    
    st.dataframe(
        filtered_df.sort_values(by="Profit", ascending=True),
        use_container_width=True,
        column_config={
            "Sales": st.column_config.NumberColumn("Doanh thu", format="$%,.2f"),
            "Profit": st.column_config.NumberColumn("Lợi nhuận ròng", format="$%,.2f"),
            "Discount": st.column_config.NumberColumn("Chiết khấu áp dụng", format="%.2f")
        }
    )
    
    st.markdown("---")
    st.info("💡 **Khuyến nghị chiến lược cho Hội đồng quản trị (Mục 5.5):** Dữ liệu chẩn đoán tại **Tab 2** chứng minh chính sách chiết khấu quá tay (Discount > 40%) là nguyên nhân chính đẩy nhóm mặt hàng Tables và Bookcases rơi vào vùng báo động đỏ (Thua lỗ ròng nặng). Khuyến nghị thắt chặt biên độ chiết khấu tối đa xuống mức 15% tại khu vực Central và South.")
