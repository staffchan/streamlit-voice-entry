import streamlit as st
import pandas as pd
import io

st.title("📋 命数チェック＆音声修正システム")

# Excelファイルアップロード
uploaded_file = st.file_uploader("📂 命数入りのExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("✅ 読み込んだデータの中身：")
    st.write(df.head())  # ← これを追加

    st.success("✅ ファイルを読み込みました！")

    # セッション状態で修正用データを保持
    if "fix_data" not in st.session_state:
        st.session_state.fix_data = {}

    st.markdown("### ✏️ 修正したいセルを選んで入力してください")

    for row_idx in range(len(df)):
        day = df.iloc[row_idx, 0]  # 一番左の列が「日」
        cols = st.columns(len(df.columns) - 1)
        for col_idx, col in enumerate(df.columns[1:], start=1):  # 月ごとの列
            cell_value = df.iloc[row_idx, col_idx]
            label = f"{col}{day}日"

            with cols[col_idx - 1]:
                if pd.notna(cell_value):
                    st.markdown(f"✔️ {label}")
                    st.markdown(f"{cell_value}")
                else:
                    st.markdown(f"❌ {label}")
                    user_input = st.text_input(f"修正（{label}）", key=f"{label}_input")
                    if user_input:
                        st.session_state.fix_data[label] = user_input

    # 保存処理
    if st.button("💾 修正を反映してExcelをダウンロード"):
        for label, val in st.session_state.fix_data.items():
            # "1月3日" → 月, 日に分解
            try:
                month, day = label.replace("日", "").split("月")
                month_col = f"{month}月"
                day = int(day)
                df.loc[df["日"] == day, month_col] = val
            except Exception as e:
                st.warning(f"❗ エラーが発生しました: {e}")

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