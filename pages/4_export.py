import streamlit as st

st.title("エクスポート機能")

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from utils.styles import MAIN_CSS
    
    # CSS適用
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    
    st.info("この機能は今後実装予定です。")
    
    # 予定機能の説明
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("予定機能")
        st.write("- 債務者選択")
        st.write("- 裁判所書式テンプレート選択")
        st.write("- スプレッドシートデータの自動転記")
        st.write("- Excelファイルとしてダウンロード")
    
    with col2:
        st.subheader("対応予定書式")
        st.write("- 債権届出書")
        st.write("- 債権者一覧表")
        st.write("- 配当表")
        st.write("- その他裁判所指定書式")
    
    # 現在利用可能な代替手段
    st.markdown("---")
    st.subheader("現在の利用方法")
    st.write("1. スプレッドシート一覧から該当する債務者のシートを開く")
    st.write("2. Google Sheetsで直接データを確認・編集")
    st.write("3. 必要に応じてExcel形式でダウンロード")
    st.write("4. 裁判所書式に手動で転記")
        
except Exception as e:
    st.error(f"エラー: {e}")
    import traceback
    st.text(traceback.format_exc())
