import streamlit as st
import pandas as pd
import io

st.title("📋 命数チェック＆修正アプリ（1〜31日 × 1〜12月対応）")

uploaded_file = st.file_uploader("📂 命数入りのExcelファイルをアップロードしてください", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📌 読み込んだ列名一覧:", df.columns.tolist())

    # 1列目の結合列「日月」を「日」に置き換える処理
    df.rename(columns={df.columns[0]: "日月"}, inplace=True)
    df["日"] = df["日月"]
    df.drop(columns=["日月"], inplace=True)
    df = df.set_index("日")

    st.write("修正後のデータ：")
    st.write(df)
    
    if "status_data" not in st.session_state:
        st.session_state.status_data = {}
    
    if "fix_data" not in st.session_state:
        st.session_state.fix_data = {}

    months = sorted(
    [col for col in df.columns if col != "日月"],
    key=lambda x: int(x)
    )
    days = sorted([int(day) for day in df.index.tolist()])
    
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
        import os
        original_filename = uploaded_file.name
        base_name = os.path.splitext(original_filename)[0]
        output_name = f"{base_name}_fixed.xlsx"
        
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
            file_name=output_name,  # ← ここが変更ポイント！
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
