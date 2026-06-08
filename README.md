Real-Time Life Monitoring & Behavioral Analytics System

A Streamlit-based personal analytics dashboard that tracks daily lifestyle habits such as sleep, study, screen time, exercise, and mood. It provides AI-like insights, personalized advice, and visual analytics to help users improve productivity and lifestyle balance.

## Live Features:

## Authentication System:

User Signup & Login
Secure password hashing using bcrypt
Session-based user tracking
Daily Lifestyle Tracker

## Users can log:

Sleep hours
Study hours
Screen time
Exercise time
Mood tracking
Smart Report System

## Each entry is displayed as a detailed report card:

## Entry-wise lifestyle breakdown Overall entry score (0–100)
Status indicator:
🟢 Excellent
🟡 Good
🔴 Needs Improvement
Personalized insights
Actionable recommendations

## Analytics Dashboard

Visual insights include:

Habit trend analysis over time
Average lifestyle comparison
Mood distribution
Productivity trend tracking
AI-Like Insights Engine

## Automatically generates suggestions like:

Improve sleep consistency
Reduce screen time
Increase study hours
Add physical exercise
Stress management tips

## Data Management:

Add daily entries
Delete specific entries
Auto-reset entry IDs when database is empty

## Tech Stack:

Frontend: Streamlit
Backend: Python
Database: SQLite
Data Handling: Pandas
Visualization: Plotly Express
Security: bcrypt password hashing

## Project Structure:
app.py              # Main Streamlit application
lifestyle.db        # SQLite database (auto-generated)
requirements.txt    # Dependencies
