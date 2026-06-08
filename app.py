import streamlit as st
import sqlite3
import bcrypt
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Real-Time Life Monitoring System", layout="wide")

DB = "lifestyle.db"

# ---------------- DATABASE ----------------
def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS lifestyle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sleep REAL,
            study REAL,
            screen REAL,
            exercise REAL,
            mood TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- RESET ID SYSTEM ----------------
def reset_id_if_empty():
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM lifestyle")
    count = c.fetchone()[0]

    if count == 0:
        c.execute("DELETE FROM sqlite_sequence WHERE name='lifestyle'")

    conn.commit()
    conn.close()

# ---------------- AUTH ----------------
def signup(username, password):
    conn = get_conn()
    c = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hashed))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def login(username, password):
    conn = get_conn()
    c = conn.cursor()

    c.execute("SELECT id, password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()

    if row:
        user_id, hashed = row
        if bcrypt.checkpw(password.encode(), hashed):
            return user_id
    return None

# ---------------- DATA ----------------
def add_entry(user_id, sleep, study, screen, exercise, mood):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO lifestyle (user_id, sleep, study, screen, exercise, mood)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, sleep, study, screen, exercise, mood))

    conn.commit()
    conn.close()

    reset_id_if_empty()

def delete_entry(entry_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM lifestyle WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()

    reset_id_if_empty()

def load_data(user_id):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM lifestyle WHERE user_id=? ORDER BY id",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df

# ---------------- SESSION ----------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------------- LOGIN UI ----------------
if st.session_state.user_id is None:
    st.title("Real-Time Life Monitoring and Behavioral Analytics System")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")

        if st.button("Login"):
            uid = login(u, p)
            if uid:
                st.session_state.user_id = uid
                st.session_state.username = u
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        su = st.text_input("Create Username", key="su_u")
        sp = st.text_input("Create Password", type="password", key="su_p")

        if st.button("Signup"):
            if signup(su, sp):
                st.success("Account created")
            else:
                st.error("Username already exists")

    st.stop()

# ---------------- LOGGED IN ----------------
user_id = st.session_state.user_id
username = st.session_state.username

st.sidebar.success(f"{username}")

if st.sidebar.button("Logout"):
    st.session_state.user_id = None
    st.rerun()

# ---------------- INPUT ----------------
st.sidebar.title("Daily Tracker")

sleep = st.sidebar.slider("Sleep Hours", 0, 24, 6)
study = st.sidebar.slider("Study Hours", 0, 24, 4)
screen = st.sidebar.slider("Screen Time", 0, 24, 5)
exercise = st.sidebar.slider("Exercise (Hours)", 0.0, 12.0, 1.0)
mood = st.sidebar.selectbox("Mood", ["Happy", "Neutral", "Stressed", "Tired"])

if st.sidebar.button("Add Entry"):
    add_entry(user_id, sleep, study, screen, exercise, mood)
    st.sidebar.success("Saved!")

# ---------------- LOAD DATA ----------------
df = load_data(user_id)

if df.empty:
    st.warning("No data yet.")
    st.stop()

# ---------------- DELETE ENTRY ----------------
st.sidebar.markdown("---")
st.sidebar.subheader("Delete Entry")

entry_to_delete = st.sidebar.selectbox("Select Entry ID", df["id"].tolist())

if st.sidebar.button("Delete Entry"):
    delete_entry(entry_to_delete)
    st.sidebar.success("Deleted!")
    st.rerun()

# ---------------- PRODUCTIVITY ----------------
df["productivity"] = (
    df["study"] * 2 +
    df["exercise"] * 3 +
    df["sleep"] -
    df["screen"]
)

# ---------------- SCORES ----------------
avg_sleep = df["sleep"].mean()
avg_study = df["study"].mean()
avg_screen = df["screen"].mean()
avg_ex = df["exercise"].mean()

sleep_score = min(avg_sleep / 8 * 100, 100)
study_score = min(avg_study / 6 * 100, 100)
fitness_score = min(avg_ex / 2 * 100, 100)
screen_score = max(100 - avg_screen * 10, 0)

overall = (sleep_score + study_score + fitness_score + screen_score) / 4

# ---------------- UI ----------------
st.title("Real-Time Life Monitoring and Behavioral Analytics System")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Sleep", f"{sleep_score:.0f}/100")
col2.metric("Study", f"{study_score:.0f}/100")
col3.metric("Fitness", f"{fitness_score:.0f}/100")
col4.metric("Screen", f"{screen_score:.0f}/100")

st.progress(int(overall))

if overall > 80:
    st.success("Excellent lifestyle balance")
elif overall > 60:
    st.warning("Needs improvement")
else:
    st.error("Critical imbalance")

st.markdown("---")

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["Overview", "Analytics", "Insights"])

# ---------------- OVERVIEW (FINAL REPORT STYLE) ----------------
with tab1:
    st.subheader("Detailed Lifestyle Report Card")

    df_sorted = df.sort_values("id", ascending=False)

    for _, row in df_sorted.iterrows():

        st.markdown(f"## Entry:{row['id']}")
        st.write(f"**Mood:** {row['mood']}")
        st.markdown("---")

        # entry scores
        sleep_s = min(row["sleep"] / 8 * 100, 100)
        study_s = min(row["study"] / 6 * 100, 100)
        fitness_s = min(row["exercise"] / 2 * 100, 100)
        screen_s = max(100 - row["screen"] * 10, 0)

        entry_score = (sleep_s + study_s + fitness_s + screen_s) / 4

        if entry_score >= 80:
            status = "🟢 Excellent"
        elif entry_score >= 60:
            status = "🟡 Good"
        else:
            status = "🔴 Needs Improvement"

        st.metric("Entry Score", f"{entry_score:.0f}/100", status)

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Sleep", f"{row['sleep']} hrs", f"{sleep_s:.0f}/100")
        c2.metric("Study", f"{row['study']} hrs", f"{study_s:.0f}/100")
        c3.metric("Screen", f"{row['screen']} hrs", f"{screen_s:.0f}/100")
        c4.metric("Exercise", f"{row['exercise']} hrs", f"{fitness_s:.0f}/100")

        st.markdown("### Insights")

        insights = []

        if sleep_s < 60:
            insights.append("Poor sleep affecting recovery")
        if study_s < 50:
            insights.append("Low study consistency")
        if screen_s < 50:
            insights.append("High screen time")
        if fitness_s < 50:
            insights.append("Low physical activity")

        if not insights:
            insights.append("Balanced lifestyle in this entry")

        for i in insights:
            st.info(i)

        st.markdown("### Action Plan")

        actions = []

        if row["sleep"] < 6:
            actions.append("Sleep 7–8 hours daily")
        if row["study"] < 3:
            actions.append("Increase study time")
        if row["screen"] > 7:
            actions.append("Reduce screen usage")
        if row["exercise"] < 1:
            actions.append("Add daily exercise")
        if row["mood"] == "Stressed":
            actions.append("Practice relaxation")

        if not actions:
            actions.append("Maintain current routine")

        for a in actions:
            st.success(a)

        st.markdown("---")

# ---------------- ANALYTICS ----------------
with tab2:
    st.subheader("Lifestyle Trends Analysis")

    avg_data = pd.DataFrame({
        "Metric": ["Sleep", "Study", "Screen", "Exercise"],
        "Hours": [df["sleep"].mean(), df["study"].mean(),
                  df["screen"].mean(), df["exercise"].mean()]
    })

    st.plotly_chart(px.bar(avg_data, x="Metric", y="Hours",
                           text_auto=True,
                           title="Average Lifestyle Breakdown"),
                    use_container_width=True)

    mood_df = df["mood"].value_counts().reset_index()
    mood_df.columns = ["Mood", "Count"]

    st.plotly_chart(px.pie(mood_df, names="Mood", values="Count",
                           title="Mood Distribution"),
                    use_container_width=True)

# ---------------- INSIGHTS ----------------
with tab3:
    st.subheader("Guide")

    tips = []

    if avg_sleep < 6:
        tips.append("Sleep 7–8 hours daily")
    if avg_study < 3:
        tips.append("Increase study consistency")
    if avg_screen > 7:
        tips.append("Reduce screen time")
    if avg_ex < 2:
        tips.append("Add exercise")

    if not tips:
        tips.append("Great balance!")

    for t in tips:
        st.info(t)

    st.subheader("Daily Plan")

    for p in [
        "Drink 2–3L water",
        "10 min mindfulness",
        "Avoid phone first 1 hour"
    ]:
        st.write("✔️", p)