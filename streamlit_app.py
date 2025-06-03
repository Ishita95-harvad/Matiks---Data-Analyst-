import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.cluster import KMeans

# Load data
df = pd.read_csv('Matiks - Data Analyst Data - Sheet1.csv')
df['Signup_Date'] = pd.to_datetime(df['Signup_Date'])
df['Last_Login'] = pd.to_datetime(df['Last_Login'])

# Dashboard Title
st.title("Matiks Gaming Analytics Dashboard")

# DAU/WAU/MAU Calculation
st.header("Active Users")
date_range = st.date_input("Select Date Range", [df['Last_Login'].min(), df['Last_Login'].max()])
df_filtered = df[(df['Last_Login'] >= pd.to_datetime(date_range[0])) & (df['Last_Login'] <= pd.to_datetime(date_range[1]))]

dau = df_filtered.groupby(df_filtered['Last_Login'].dt.date)['User_ID'].nunique()
wau = df_filtered.groupby(df_filtered['Last_Login'].dt.isocalendar().week)['User_ID'].nunique()
mau = df_filtered.groupby(df_filtered['Last_Login'].dt.to_period('M'))['User_ID'].nunique()

st.metric("DAU", dau.mean().round(2))
st.metric("WAU", wau.mean().round(2))
st.metric("MAU", mau.mean().round(2))

# Revenue Trends
st.header("Revenue Trends")
granularity = st.selectbox("Select Time Granularity", ["Daily", "Weekly", "Monthly"])
if granularity == "Daily":
    revenue_trend = df_filtered.groupby(df_filtered['Last_Login'].dt.date)['Total_Revenue_USD'].sum()
elif granularity == "Weekly":
    revenue_trend = df_filtered.groupby(df_filtered['Last_Login'].dt.isocalendar().week)['Total_Revenue_USD'].sum()
else:
    revenue_trend = df_filtered.groupby(df_filtered['Last_Login'].dt.to_period('M'))['Total_Revenue_USD'].sum()

fig = px.line(x=revenue_trend.index, y=revenue_trend.values, title="Revenue Over Time")
st.plotly_chart(fig)

# Breakdowns
st.header("Revenue Breakdowns")
breakdown_by = st.selectbox("Breakdown By", ["Device_Type", "Subscription_Tier", "Preferred_Game_Mode"])
fig = px.bar(df_filtered, x=breakdown_by, y="Total_Revenue_USD", title=f"Revenue by {breakdown_by}")
st.plotly_chart(fig)

# Behavioral Patterns
st.header("Behavioral Patterns")
fig = px.scatter(df_filtered, x="Total_Play_Sessions", y="Avg_Session_Duration_Min", color="Subscription_Tier",
                 title="Session Frequency vs Duration")
st.plotly_chart(fig)

# Churn Analysis
st.header("Churn Indicators")
df_filtered['Time_Gap'] = (df_filtered['Last_Login'] - df_filtered['Signup_Date']).dt.days
fig = px.histogram(df_filtered, x="Time_Gap", title="Time Gap Between Signup and Last Login")
st.plotly_chart(fig)

# Cohort Analysis
st.header("Cohort Analysis")
cohorts = df.groupby(df['Signup_Date'].dt.to_period('M'))['User_ID'].nunique()
retention = df.groupby([df['Signup_Date'].dt.to_period('M'), df['Last_Login'].dt.to_period('M')])['User_ID'].nunique().unstack()
st.write(retention)

# Funnel Tracking
st.header("Funnel Tracking")
funnel_data = {
    "Stage": ["Signup", "First Game", "Repeat Session"],
    "Count": [df['User_ID'].nunique(), df[df['Total_Play_Sessions'] >= 1]['User_ID'].nunique(),
              df[df['Total_Play_Sessions'] > 1]['User_ID'].nunique()]
}
fig = go.Figure(go.Funnel(y=funnel_data["Stage"], x=funnel_data["Count"]))
st.plotly_chart(fig)

# Clustering
st.header("User Segmentation")
X = df[['Total_Revenue_USD', 'Total_Play_Sessions']].values
kmeans = KMeans(n_clusters=3).fit(X)
df['Cluster'] = kmeans.labels_
fig = px.scatter(df, x="Total_Revenue_USD", y="Total_Play_Sessions", color="Cluster", title="User Segmentation")
st.plotly_chart(fig)
