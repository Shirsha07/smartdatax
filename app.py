import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SmartDataX", layout="wide")

# ---------------- 🎨 UI ----------------
st.markdown("""
<style>
body { background-color: #0f172a; }
h1, h2, h3 { color: #e2e8f0; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1e293b, #334155);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
section[data-testid="stSidebar"] { background-color: #020617; }
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<h1 style='text-align:center; color:#38bdf8;'>🚀 SmartDataX</h1>
<p style='text-align:center;'>From Data → Insights → Decisions</p>
""", unsafe_allow_html=True)

st.markdown("### 📊 A Unified Platform for Business Intelligence & Decision Making")

# ---------------- LOAD DATA ----------------
data = pd.read_csv("train.csv")
data.columns = data.columns.str.title()
data['Order Date'] = pd.to_datetime(data['Order Date'], dayfirst=True)

# ---------------- FILTERS ----------------
st.sidebar.header("🔍 Filters")

date_range = st.sidebar.date_input(
    "Date Range",
    [data['Order Date'].min(), data['Order Date'].max()]
)

region = st.sidebar.multiselect("Region", data['Region'].unique(), default=data['Region'].unique())
category = st.sidebar.multiselect("Category", data['Category'].unique(), default=data['Category'].unique())
segment = st.sidebar.multiselect("Segment", data['Segment'].unique(), default=data['Segment'].unique())
ship_mode = st.sidebar.multiselect("Ship Mode", data['Ship Mode'].unique(), default=data['Ship Mode'].unique())
sub_category = st.sidebar.multiselect("Sub-Category", data['Sub-Category'].unique(), default=data['Sub-Category'].unique())

filtered_data = data[
    (data['Order Date'] >= pd.to_datetime(date_range[0])) &
    (data['Order Date'] <= pd.to_datetime(date_range[1])) &
    (data['Region'].isin(region)) &
    (data['Category'].isin(category)) &
    (data['Segment'].isin(segment)) &
    (data['Ship Mode'].isin(ship_mode)) &
    (data['Sub-Category'].isin(sub_category))
]

# ---------------- KPI ----------------
st.markdown("## 📊 Business Overview")

total_sales = int(filtered_data['Sales'].sum())
avg_sales = int(filtered_data['Sales'].mean())
max_sales = int(filtered_data['Sales'].max())
orders = filtered_data.shape[0]

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Revenue", f"₹ {total_sales}")
c2.metric("📦 Orders", orders)
c3.metric("📊 Avg Sales", f"₹ {avg_sales}")
c4.metric("🔥 Peak Sales", f"₹ {max_sales}")

# ---------------- DAILY SALES ----------------
daily_sales = filtered_data.groupby('Order Date')['Sales'].sum().reset_index()

# ---------------- SALES COMPARISON ----------------
st.markdown("## 📊 Sales Comparison")

recent_sales = daily_sales.tail(7)['Sales'].sum()
previous_sales = daily_sales.iloc[-14:-7]['Sales'].sum()
growth = ((recent_sales - previous_sales) / previous_sales) * 100 if previous_sales != 0 else 0

st.metric("📈 Weekly Growth", f"{growth:.2f}%")

# ---------------- CHARTS ----------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("## 📈 Sales Trend")
    st.caption("Tracks revenue movement over time to identify trends and seasonal patterns.")
    fig = px.area(daily_sales, x='Order Date', y='Sales', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("## 🌍 Region Performance")
    region_data = filtered_data.groupby('Region')['Sales'].sum().reset_index()
    fig2 = px.bar(region_data, x='Region', y='Sales', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.markdown("## 📦 Category Performance")
    cat_data = filtered_data.groupby('Category')['Sales'].sum().reset_index()
    fig3 = px.pie(cat_data, names='Category', values='Sales', template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("## 🏆 Top Products")
    top_products = filtered_data.groupby('Product Name')['Sales'].sum().reset_index().nlargest(5, 'Sales')
    fig4 = px.bar(top_products, x='Product Name', y='Sales', template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

# ---------------- FORECAST ----------------
st.markdown("## 🔮 Sales Forecast")

forecast = daily_sales['Sales'].rolling(7).mean()

fig_forecast = px.line(daily_sales, x='Order Date', y='Sales', template="plotly_dark")
fig_forecast.add_scatter(
    x=daily_sales['Order Date'],
    y=forecast,
    mode='lines',
    name='Forecast',
    line=dict(dash='dash')
)

st.plotly_chart(fig_forecast, use_container_width=True)
st.caption("Forecast is based on rolling average of recent sales trends.")

# ---------------- FORECAST SUMMARY ----------------
st.markdown("### 📖 Forecast Summary")

latest_forecast = forecast.iloc[-1]
avg_sales_val = daily_sales['Sales'].mean()

if latest_forecast > avg_sales_val:
    st.success("📈 Sales are expected to grow steadily. Scale inventory and operations.")
elif latest_forecast < avg_sales_val:
    st.warning("📉 Sales may decline. Strengthen marketing and promotions.")
else:
    st.info("📊 Sales expected to remain stable.")

if growth > 0:
    st.info("📊 Positive momentum detected.")
else:
    st.warning("⚠️ Declining momentum detected.")

st.info("💡 Align marketing and inventory with forecast trends.")

# ---------------- GAINERS / LOSERS ----------------
st.markdown("## 📊 Top Gainers & Losers")

recent = filtered_data[filtered_data['Order Date'] >= filtered_data['Order Date'].max() - pd.Timedelta(days=7)]
prev = filtered_data[
    (filtered_data['Order Date'] < filtered_data['Order Date'].max() - pd.Timedelta(days=7)) &
    (filtered_data['Order Date'] >= filtered_data['Order Date'].max() - pd.Timedelta(days=14))
]

recent_sales = recent.groupby('Product Name')['Sales'].sum()
prev_sales = prev.groupby('Product Name')['Sales'].sum()

comparison = pd.DataFrame({'Recent': recent_sales, 'Previous': prev_sales}).fillna(0)
comparison['Growth'] = comparison['Recent'] - comparison['Previous']

gainers = comparison.sort_values('Growth', ascending=False).head(5)
losers = comparison.sort_values('Growth').head(5)

c5, c6 = st.columns(2)

c5.markdown("### 🚀 Top Gainers")
c5.dataframe(gainers.style.highlight_max(axis=0))

c6.markdown("### 📉 Top Losers")
c6.dataframe(losers.style.highlight_min(axis=0))

# ---------------- ALERTS ----------------
st.markdown("## 🚨 Smart Alerts")

if growth < 0:
    st.error("⚠️ Sales declining — immediate strategic intervention required.")

if total_sales > avg_sales * 100:
    st.success("🔥 Strong revenue performance detected.")

# ---------------- INSIGHTS ----------------
st.markdown("## 📖 Insights")

top_region = region_data.loc[region_data['Sales'].idxmax(), 'Region']
top_category = cat_data.loc[cat_data['Sales'].idxmax(), 'Category']

st.info(f"🌍 Top Region: {top_region}")
st.info(f"📦 Best Category: {top_category}")

# ---------------- DECISION PANEL ----------------
st.markdown("## 🧠 Decision Intelligence")
st.caption("System-generated actionable insights for decision-makers.")

st.success("📌 Focus marketing on high-performing regions")
st.success("📌 Increase promotions if sales drop")
st.success("📌 Optimize inventory for top products")
st.success("📌 Improve customer targeting strategies")

# ---------------- HEALTH SCORE ----------------
st.markdown("## 🔍 Business Health Score")

health_score = int((avg_sales / max_sales) * 100)
health_score = max(0, min(health_score, 100))

st.progress(health_score)
st.write(f"### {health_score}% Performance")

st.caption("Represents overall business performance based on sales efficiency.")

if health_score > 70:
    st.success("🟢 Business is performing well")
elif health_score > 40:
    st.warning("🟡 Moderate performance")
else:
    st.error("🔴 Needs improvement")

# ---------------- IMPROVEMENTS ----------------
st.markdown("### 💡 Improvement Suggestions")

if health_score < 50:
    st.error("""
🔴 Increase promotions  
🔴 Improve customer targeting  
🔴 Optimize pricing strategy  
""")
elif health_score < 70:
    st.warning("""
🟡 Improve marketing efficiency  
🟡 Optimize inventory  
🟡 Focus on strong segments  
""")
else:
    st.success("""
🟢 Scale high-performing products  
🟢 Expand markets  
🟢 Increase engagement  
""")

# ---------------- CONCLUSION ----------------
st.markdown("---")
st.markdown("### 🚀 Conclusion")

st.success("""
This system transforms data into actionable insights, enabling proactive decision-making and business growth.
""")
