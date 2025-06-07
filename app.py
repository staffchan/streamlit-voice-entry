import streamlit as st
import pandas as pd
import io

st.title("📋 命数チェック＆修正アプリ（全日対応）")

uploaded_file = st.file_uploader("📂 命数入りのExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns.values[0] = "日"  # 1列目を「日」に補正
    st.success("✅ データを読み込みました！")

    # 修正入力保持用のセッションステート初期化
    if "fix_data" not in st.session_state:
        st.session_state.fix_data = {}

    if "status_data" not in st.session_state:
        st.session_state.status_data = {}

    st.markdown("### ✏️ 各セルについて『OK or 修正』を選んで、必要な箇所のみ修正してください")

    # 表の構造：縦が日（1〜31）、横が「1月」〜「12月」
    for day in df["日"]:
        cols = st.columns(len(df.columns) - 1)
        for col_idx, month in enumerate(df.columns[1:], start=1):
            cell_value = df.loc[df["日"] == day, month].values[0]
            label = f"{month}{day}日"
            key_status = f"status_{label}"
            key_input = f"input_{label}"

            with cols[col_idx - 1]:
                status = st.radio(
                    f"{label}",
                    ["OK", "修正"],
                    key=key_status,
                    horizontal=True,
                )
                st.session_state.status_data[label] = status

                if status == "修正":
                    user_input = st.text_input(f"入力（{label}）", key=key_input)
                    if user_input:
                        st.session_state.fix_data[label] = user_input

    # 保存ボタン処理
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