import streamlit as st
import pandas as pd
import io

st.title("📋 命数チェック＆修正アプリ（1〜31日 × 1〜12月対応）")

uploaded_file = st.file_uploader("📂 命数入りのExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns.values[0] = "日"  # 1列目を「日」に固定
    st.success("✅ データを読み込みました！")

    if "fix_data" not in st.session_state:
        st.session_state.fix_data = {}
    if "status_data" not in st.session_state:
        st.session_state.status_data = {}

    st.markdown("### ✏️ 各セルについて『OK or 修正』を選んで、現在の命数を確認・必要な箇所のみ修正してください")

    months = df.columns[1:]

    for day in range(1, 32):  # ← ここが大事！！
        for month in months:
            label = f"{month}{day}日"
            key_base = f"{month}_{day}"
            try:
                cell_value = df.loc[df["日"] == day, month].values[0]
                current_value = str(cell_value) if pd.notna(cell_value) and str(cell_value).strip() != "" else "（空）"
            except:
                current_value = "（取得エラー）"

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
                df.loc[df["日"] == day, month_col] = val
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