st.image("037DCF7B-ECED-422C-AABE-BD40863A0B37_1_201_a.jpeg", width=200)
st.title("HappinessAC 得点計算アプリ")

import streamlit as st
import pandas as pd

# 得点計算関数（種目ごとの計算式）
def calculate_score(event, record):
    if event == "100m":
        return max(int(-155 * record + 3250), 50)
    elif event == "800m":
        return max(int(-9.44 * record + 2500), 50)
    elif event == "80mハードル":
        return max(int(-170.94 * record + 3342.7), 50)
    elif event == "走高跳":
        return max(int(1153.8 * record - 465.38), 50)
    elif event == "走幅跳":
        return max(int(280.11 * record - 226.61), 50)
    elif event == "ジャベリックボール投":
        return max(int(20.325 * record + 60.163), 50)
    else:
        return None

# 時間入力の補助関数
def convert_time_to_seconds_100m(seconds, milliseconds):
    return seconds + milliseconds / 100

def convert_time_to_seconds_800m(minutes, seconds, milliseconds):
    return minutes * 60 + seconds + milliseconds / 100

# 得点早見表の生成関数
def generate_score_table(event):
    if event == "100m":
        records = [i / 100 for i in range(1100, 1701)]
        display_records = [f"{r:.2f}" for r in records]

    elif event == "800m":
        records = [i / 100 for i in range(12000, 30001, 10)]

        def format_time(sec):
            m = int(sec // 60)
            s = int(sec % 60)
            ms = int(round((sec - int(sec)) * 100))
            return f"{m}:{s:02}.{ms:02}"

        display_records = [format_time(r) for r in records]

    elif event == "80mハードル":
        records = [i / 100 for i in range(1100, 1901)]
        display_records = [f"{r:.2f}" for r in records]

    elif event == "走高跳":
        records = [i / 100 for i in range(100, 201)]
        display_records = [f"{r:.2f}" for r in records]

    elif event == "走幅跳":
        records = [i / 100 for i in range(200, 651)]
        display_records = [f"{r:.2f}" for r in records]

    elif event == "ジャベリックボール投":
        records = [i / 100 for i in range(1000, 5501, 10)]
        display_records = [f"{r:.2f}" for r in records]

    else:
        return pd.DataFrame()

    scores = [calculate_score(event, r) for r in records]
    return pd.DataFrame({
        "記録": display_records,
        "得点": scores
    })

# Streamlit アプリ UI
st.title("小学生陸上競技 得点計算アプリ")

tab1, tab2 = st.tabs(["📋 得点早見表", "🧮 得点計算"])

# 📋 得点早見表
with tab1:
    st.subheader("種目を選択してください")
    event_table = st.selectbox("種目を選択（早見表）", ["100m", "800m", "80mハードル", "走高跳", "走幅跳", "ジャベリックボール投"])
    table_df = generate_score_table(event_table)
    st.dataframe(table_df, use_container_width=True)

# 🧮 得点計算
with tab2:
    st.subheader("記録を入力してください")
    event_calc = st.selectbox(
        "種目を選択（計算）",
        ["100m", "800m", "80mハードル", "走高跳", "走幅跳", "ジャベリックボール投", "コンバインドA", "コンバインドB"],
        key="event_calc"
    )

    if event_calc == "100m":
        col1, col2 = st.columns(2)
        sec = col1.number_input("秒", min_value=0, step=1, value=13)
        ms = col2.number_input("ミリ秒", min_value=0, max_value=99, step=1, value=12)
        record = convert_time_to_seconds_100m(sec, ms)
        score = calculate_score("100m", record)
        st.success(f"得点: {score} 点")

    elif event_calc == "800m":
        col1, col2, col3 = st.columns(3)
        min = col1.number_input("分", min_value=0, step=1, value=2)
        sec = col2.number_input("秒", min_value=0, max_value=59, step=1, value=15)
        ms = col3.number_input("ミリ秒", min_value=0, max_value=99, step=1, value=0)
        record = convert_time_to_seconds_800m(min, sec, ms)
        score = calculate_score("800m", record)
        st.success(f"得点: {score} 点")

    elif event_calc == "コンバインドA":
        st.subheader("【コンバインドA】80mハードル + 走高跳")

        col1, col2 = st.columns(2)
        h_sec = col1.number_input("80mH：秒", min_value=0, step=1, value=13)
        h_ms = col2.number_input("80mH：ミリ秒", min_value=0, max_value=99, step=1, value=0)
        h_record = convert_time_to_seconds_100m(h_sec, h_ms)
        h_score = calculate_score("80mハードル", h_record)

        hj_record = st.number_input("走高跳：記録 (m)", min_value=0.0, step=0.01)
        hj_score = calculate_score("走高跳", hj_record)

        total = h_score + hj_score
        st.info(f"80mH得点：{h_score} 点")
        st.info(f"走高跳得点：{hj_score} 点")
        st.success(f"合計得点：{total} 点")

    elif event_calc == "コンバインドB":
        st.subheader("【コンバインドB】走幅跳 + ジャベリックボール投")

        lj_record = st.number_input("走幅跳：記録 (m)", min_value=0.0, step=0.01)
        lj_score = calculate_score("走幅跳", lj_record)

        jt_record = st.number_input("ジャベリックボール投：記録 (m)", min_value=0.0, step=0.01)
        jt_score = calculate_score("ジャベリックボール投", jt_record)

        total = lj_score + jt_score
        st.info(f"走幅跳得点：{lj_score} 点")
        st.info(f"ジャベリック得点：{jt_score} 点")
        st.success(f"合計得点：{total} 点")

    else:
        record = st.number_input("記録を入力 (m または 秒)", min_value=0.0, step=0.01)
        score = calculate_score(event_calc, record)
        if score is not None:
            st.success(f"得点: {score} 点")
        else:
            st.error("計算できませんでした")

