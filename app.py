import streamlit as st
import pandas as pd
import io

# セッションステートの初期化
if 'date_index' not in st.session_state:
    st.session_state.date_index = 0
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'edit_date' not in st.session_state:
    st.session_state.edit_date = None

# 月日データの順序リスト（1月1日〜12月31日）
months_days = [(m, d) for m in range(1, 13) for d in range(1, 32)
               if not (m == 2 and d > 29) and not (m in [4, 6, 9, 11] and d > 30)]

# ─────────────────────
# サイドバーでファイルアップロード
st.sidebar.header("📂 Excelファイルの読み込み")
uploaded_file = st.sidebar.file_uploader("保存したExcelファイルをアップロード", type=["xlsx"])

# ファイルがあるときだけ読み込み処理を行う
if uploaded_file is not None:
    df_uploaded = pd.read_excel(uploaded_file)
    new_data = {}

    day_column = df_uploaded.columns[0]

    for idx, row in df_uploaded.iterrows():
        day = int(row[day_column])
        for col in df_uploaded.columns:
            if col is None or pd.isna(col):
                continue

            col_str = str(col)
            if col_str.endswith("月") and col_str.replace("月", "").isdigit():
                if pd.notna(row[col]):
                    date_key = f"{col_str}{day}日"
                    new_data[date_key] = str(row[col])

    st.session_state.data = new_data

    # 次の未入力日付を探す
    for i, (m, d) in enumerate(months_days):
        if f"{m}月{d}日" not in new_data:
            st.session_state.date_index = i
            break
    else:
        st.session_state.date_index = len(months_days)

    st.sidebar.success("✅ データを読み込みました！")
# ─────────────────────
# メイン表示エリア
st.title("📅 日付順音声入力アプリ（読み込み対応）")

# 現在の入力対象日付
if st.session_state.edit_date:
    current_date_str = st.session_state.edit_date
    current_month, current_day = map(int, current_date_str.replace("月", ".").replace("日", "").split("."))
    st.markdown(f"### 🔁 修正中：**{current_date_str}**")
elif st.session_state.date_index < len(months_days):
    current_month, current_day = months_days[st.session_state.date_index]
    current_date_str = f"{current_month}月{current_day}日"
    st.markdown(f"### 現在入力中：**{current_date_str}**")
else:
    current_date_str = None
    st.success("🎉 入力が完了しました！")

# ─────────────────────
# 入力欄
if current_date_str:
    default_val = st.session_state.data.get(current_date_str, "").replace(".", " ") if st.session_state.edit_date else ""
    user_input = st.text_input("🎙️ 数字をスペース区切りで入力してください（例：44 43 48）", value=default_val, key=current_date_str)

    if st.button("✅ 登録して次へ"):
        if user_input.strip() != "":
            st.session_state.data[current_date_str] = user_input.strip().replace(" ", ".")
            st.session_state.edit_date = None
            st.session_state.date_index += 1
            st.rerun()

# ─────────────────────
# 入力済み一覧 + 修正ボタン
st.markdown("---")
st.markdown("#### 📝 入力済み一覧")

for date in sorted(
    st.session_state.data.keys(),
    key=lambda x: (
        int(x.replace("月", ".").replace("日", "").split(".")[0]),
        int(x.replace("月", ".").replace("日", "").split(".")[1])
    )
):
    value = st.session_state.data[date]
    cols = st.columns([3, 1])
    cols[0].markdown(f"- {date}: {value}")
    if cols[1].button("✏️ 修正", key=f"edit_{date}"):
        st.session_state.edit_date = date
        st.rerun()

# ─────────────────────
# Excel出力（途中でもOK）
if len(st.session_state.data) > 0:
    df_out = pd.DataFrame(index=range(1, 32), columns=[f"{m}月" for m in range(1, 13)])
    for date_str, value in st.session_state.data.items():
        m, d = map(int, date_str.replace("月", ".").replace("日", "").split("."))
        df_out.at[d, f"{m}月"] = value
    df_out.insert(0, "日", df_out.index)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_out.to_excel(writer, index=False, sheet_name="1930年")
    output.seek(0)

    st.download_button(
        label="📥 Excelファイルをダウンロード（途中保存OK）",
        data=output,
        file_name="gosei_1930_partial.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
