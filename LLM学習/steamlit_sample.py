import streamlit as st

st.title("筋トレメニュー自動生成アプリ")
st.write("トレーニング目的を選んでください。")

goal = st.selectbox("目的", ["筋肥大", "ダイエット", "健康維持"])

if st.button("メニューを生成"):
    if goal == "筋肥大":
        st.write("・ベンチプレス3セット\n・スクワット3セット\n・デッドリフト3セット")
    elif goal == "ダイエット":
        st.write("・ジャンピングスクワット5セット\n・バーピー20回\n・ランジ3セット")
    else:
        st.write("・ウォーキング30分\n・プランク60秒\n・スクワット20回")
