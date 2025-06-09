import streamlit as st
import pandas as pd
import io

st.title("📋 命数チェック＆修正アプリ（1〜31日 × 1〜12月対応）")

uploaded_file = st.file_uploader("📂 命数入りのExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns.values[0] = "日"  # 先に列名を「日」に変える
    df = df.set_index("日")     # そのあと index に設定！！
    
    if "status_data" not in st.session_state:
        st.session_state.status_data = {}
    
    if "fix_data" not in st.session_state:
        st.session_state.fix_data = {}

    months = sorted(df.columns, key=lambda x: int(x.replace("月", "")))  # 月（1〜12）
    days = sorted(df.index.tolist())  # 日（1〜31）

    for month in months:
        for day in days:
            try:
                cell_value = df.at[day, month]
                current_value = str(cell_value)
            except:
                current_value = "(取得エラー)"

            label = f"{month}{day}日"
            key_base = f"{month}_{day}"

            st.write(f"📅 **{label}**　🧮 現在の命数：`{current_value}`")
            status = st.radio(
                f"選択：{label}",
                ["OK", "修正"],
                key=f"radio_{key_base}",
                horizontal=True
            )
            st.session_state.status_data[label] = status

            if status == "修正":
                user_input = st.text_input(f"✏️ 新しい命数を入力（{label}）", key=f"input_{key_base}")
                if user_input:
                    st.session_state.fix_data[label] = user_input
                    
    if st.button("💾 修正を反映してExcelをダウンロード"):
        for label, val in st.session_state.fix_data.items():
            try:
                month, day = label.replace("日", "").split("月")
                month_col = f"{month}月"
                day = int(day)
                df.at[day, month_col] = val
            except Exception as e:
                st.warning(f"❗ エラー（{label}）：{e}")
            
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="1930年")
        output.seek(0)

        st.download_button(
            label="📥 修正済みExcelをダウンロード",
            data=output,
            file_name="1930_fixed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
