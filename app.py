import streamlit as st
import pandas as pd
import os
from datetime import date

import plotly.express as px
import seaborn as sns
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Lifestyle Analytics", layout="wide")

DATA_FILE = "lifestyle_data.csv"

# ---------------- LOAD DATA ----------------
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return df
    else:
        return pd.DataFrame(columns=[
            "Date", "Sleep_Hours", "Study_Hours",
            "Screen_Time", "Exercise_Minutes", "Mood"
        ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df = load_data()

# ---------------- SIDEBAR INPUT ----------------
st.sidebar.title("📌 Daily Tracker")

today = str(date.today())

sleep = st.sidebar.slider("Sleep Hours", 0, 12, 6)
study = st.sidebar.slider("Study Hours", 0, 16, 4)
screen = st.sidebar.slider("Screen Time (Hours)", 0, 16, 5)
exercise = st.sidebar.slider("Exercise (Minutes)", 0, 120, 30)

mood = st.sidebar.selectbox("Mood", ["Happy", "Neutral", "Stressed", "Tired"])

if st.sidebar.button("➕ Add Entry"):
    new_data = pd.DataFrame([{
        "Date": today,
        "Sleep_Hours": sleep,
        "Study_Hours": study,
        "Screen_Time": screen,
        "Exercise_Minutes": exercise,
        "Mood": mood
    }])

    df = pd.concat([df, new_data], ignore_index=True)
    save_data(df)
    st.sidebar.success("Saved Successfully!")

# ---------------- MAIN ----------------
st.title("📊 Smart Lifestyle Analytics Dashboard")

if df.empty:
    st.warning("No data yet. Please add entries.")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"])

# ---------------- FEATURE ENGINEERING ----------------
df["Productivity_Score"] = (
    df["Study_Hours"] * 2 +
    df["Exercise_Minutes"] / 30 +
    df["Sleep_Hours"] -
    df["Screen_Time"]
)

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "🔍 Deep Analysis",
    "🧠 Insights",
    "📂 Dataset"
])

# ---------------- TAB 1: OVERVIEW ----------------
with tab1:
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Avg Sleep", f"{df['Sleep_Hours'].mean():.2f} hrs")
    col2.metric("Avg Study", f"{df['Study_Hours'].mean():.2f} hrs")
    col3.metric("Avg Screen", f"{df['Screen_Time'].mean():.2f} hrs")
    col4.metric("Avg Productivity Score", f"{df['Productivity_Score'].mean():.2f}")

    fig = px.line(df, x="Date", y=["Sleep_Hours", "Study_Hours", "Screen_Time"],
                  title="Activity Trends Over Time")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2: DEEP ANALYSIS ----------------
with tab2:
    st.subheader("📊 Filtered Analysis")

    col1, col2 = st.columns(2)

    # Date filter
    start_date = col1.date_input("Start Date", df["Date"].min())
    end_date = col2.date_input("End Date", df["Date"].max())

    mood_filter = st.multiselect(
        "Filter by Mood",
        df["Mood"].unique(),
        default=list(df["Mood"].unique())
    )

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date)) &
        (df["Mood"].isin(mood_filter))
    ]

    st.write("Filtered Data:")
    st.dataframe(filtered_df)

    fig2 = px.bar(filtered_df, x="Date", y="Productivity_Score",
                  color="Mood", title="Productivity Over Time")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- TAB 3: INSIGHTS ----------------
with tab3:
    st.subheader("🧠 AI-Generated Insights")

    avg_sleep = df["Sleep_Hours"].mean()
    avg_screen = df["Screen_Time"].mean()
    avg_study = df["Study_Hours"].mean()

    if avg_sleep < 6:
        st.warning("⚠️ Low sleep detected. It may impact productivity.")

    if avg_screen > 7:
        st.warning("📱 High screen time may reduce focus.")

    if avg_study > 5:
        st.success("📚 Strong study discipline observed.")

    st.subheader("📊 Correlation Heatmap")

    corr = df[[
        "Sleep_Hours",
        "Study_Hours",
        "Screen_Time",
        "Exercise_Minutes",
        "Productivity_Score"
    ]].corr()

    fig3 = px.imshow(corr, text_auto=True, title="Feature Correlation Heatmap")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🏆 Best Day Analysis")

    best_day = df.loc[df["Productivity_Score"].idxmax()]
    st.success(f"Most Productive Day: {best_day['Date'].date()}")

# ---------------- TAB 4: DATASET ----------------
with tab4:
    st.subheader("📂 Full Dataset")

    st.dataframe(df.sort_values("Date", ascending=False))

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇ Download Data as CSV",
        csv,
        "lifestyle_data.csv",
        "text/csv"
    )