import streamlit as st
import pandas as pd
import os
from datetime import date

# ===== 設定 =====
CSV_FILE = "score_data.csv"

# ===== 得点計算関数 =====
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
        return 0

# ===== 時間入力変換 =====
def convert_time_to_seconds(mins, secs, millis):
    return mins * 60 + secs + millis / 100

def convert_100m_time(secs, millis):
    return secs + millis / 100

# ===== CSVに保存 =====
def save_to_csv(data, filename):
    df = pd.DataFrame([data])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', header=False, index=False)
    else:
        df.to_csv(filename, index=False)

# ===== CSVから読み込み =====
def load_csv(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame()

# ===== CSVから指定行を削除 =====
def delete_row(index, filename):
    df = load_csv(filename)
    df = df.drop(index).reset_index(drop=True)
    df.to_csv(filename, index=False)

# ===== アプリUI =====
st.set_page_config(page_title="得点計算アプリ", layout="wide")
st.title("HappinessAC 得点計算アプリ")

# ===== タブ構成 =====
tab1, tab2, tab3 = st.tabs(["📋 得点早見表", "🧮 得点計算・記録入力", "📂 記録一覧表示"])

# ===== タブ1：得点早見表 =====
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
    return pd.DataFrame({"記録": display_records, "得点": scores})

with tab1:
    st.subheader("種目を選択してください")
    event_table = st.selectbox("種目を選択（早見表）", ["100m", "800m", "80mハードル", "走高跳", "走幅跳", "ジャベリックボール投"])
    table_df = generate_score_table(event_table)
    st.dataframe(table_df, use_container_width=True)

# ===== タブ2：得点計算・記録入力 =====
with tab2:
    st.subheader("記録を入力して保存")
    name = st.text_input("名前")
    grade = st.text_input("学年")
    date_input = st.date_input("日付", value=date.today())
    event = st.selectbox("種目", ["100m", "800m", "80mハードル", "走高跳", "走幅跳", "ジャベリックボール投"])

    if event == "100m" or event == "80mハードル":
        col1, col2 = st.columns(2)
        sec = col1.number_input("秒", min_value=0, value=13)
        ms = col2.number_input("ミリ秒", min_value=0, max_value=99, value=0)
        record = convert_100m_time(sec, ms)

    elif event == "800m":
        col1, col2, col3 = st.columns(3)
        min = col1.number_input("分", min_value=0, value=2)
        sec = col2.number_input("秒", min_value=0, max_value=59, value=30)
        ms = col3.number_input("ミリ秒", min_value=0, max_value=99, value=0)
        record = convert_time_to_seconds(min, sec, ms)

    else:
        record = st.number_input("記録 (m)", min_value=0.0, step=0.01)

    score = calculate_score(event, record)
    st.info(f"得点：{score} 点")

    if st.button("この記録を保存"):
        new_data = {
            "名前": name,
            "学年": grade,
            "種目": event,
            "記録": round(record, 2),
            "得点": score,
            "日付": date_input.strftime("%Y-%m-%d")
        }
        save_to_csv(new_data, CSV_FILE)
        st.success("保存しました！")

# ===== タブ3：記録一覧表示 =====
# ===== タブ3：記録一覧表示 =====
with tab3:
    st.subheader("保存された記録一覧")
    df = load_csv(CSV_FILE)

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.subheader("削除したいデータを選んでください")

        for i, row in df.iterrows():
            with st.expander(f"{row['名前']} | {row['種目']} | {row['記録']}"):
                st.write(row.to_dict())
                if st.button("❌ この記録を削除", key=f"delete_{i}"):
                    delete_row(i, CSV_FILE)
                    st.success("削除しました")
                    st.experimental_rerun()  # ✅ 自動でページを再読み込み！
    else:
        st.info("まだ記録が保存されていません。")
