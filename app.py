import streamlit as st
import pandas as pd
import io

# セッションステートの初期化
if 'date_index' not in st.session_state:
    st.session_state.date_index = 0
if 'data' not in st.session_state:
    st.session_state.data = {}
if 'edit_date' not in st.session_state:
    st.session_state.edit_date = None  # 修正対象日付

# 有効な月日（1月1日〜12月31日まで）
months_days = [(m, d) for m in range(1, 13) for d in range(1, 32)
               if not (m == 2 and d > 29) and not (m in [4, 6, 9, 11] and d > 30)]

# タイトル
st.title("📅 日付順音声入力アプリ（修正機能付き）")

# 修正中の日付があれば、それを優先表示
if st.session_state.edit_date:
    current_date_str = st.session_state.edit_date
    current_month, current_day = map(int, current_date_str.replace("月", ".").replace("日", "").split("."))
    st.markdown(f"### 🔁 修正中：**{current_date_str}**")
else:
    if st.session_state.date_index < len(months_days):
        current_month, current_day = months_days[st.session_state.date_index]
        current_date_str = f"{current_month}月{current_day}日"
        st.markdown(f"### 現在入力中：**{current_date_str}**")
    else:
        current_date_str = None
        st.success("🎉 すべての入力が完了しました！以下からExcelファイルをダウンロードできます。")

# 入力欄の表示（入力中 or 修正中）
if current_date_str:
    # 修正モード中は既存の値、そうでなければ空欄（前の入力は記憶しない）
    if st.session_state.edit_date:
        default_val = st.session_state.data.get(current_date_str, "").replace(".", " ")
    else:
        default_val = ""

    user_input = st.text_input("🎙️ 数字をスペース区切りで入力してください（例：44 43 48）", value=default_val, key=current_date_str)

    if st.button("✅ 登録して次へ"):
        if user_input.strip() != "":
            st.session_state.data[current_date_str] = user_input.strip().replace(" ", ".")
            if st.session_state.edit_date:
                st.session_state.edit_date = None
            else:
                st.session_state.date_index += 1
            st.rerun()

# 入力済み一覧と修正ボタン
st.markdown("---")
st.markdown("#### 📝 入力済み一覧")

# 🔽 🔧 ここで日付順にソートして表示
for date in sorted(
    st.session_state.data.keys(),
    key=lambda x: (
        int(x.replace("月", ".").replace("日", "").split(".")[0]),  # 月
        int(x.replace("月", ".").replace("日", "").split(".")[1])   # 日
    )
):
    value = st.session_state.data[date]
    cols = st.columns([3, 1])
    cols[0].markdown(f"- {date}: {value}")
    if cols[1].button("✏️ 修正", key=f"edit_{date}"):
        st.session_state.edit_date = date
        st.rerun()
        
# Excel出力（全入力完了 & 修正中でないとき）
if st.session_state.date_index >= len(months_days) and not st.session_state.edit_date:
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
        label="📥 Excelファイルをダウンロード",
        data=output,
        file_name="gosei_1930.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
