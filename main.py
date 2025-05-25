"""
債権者データ管理システム - ホームページ
"""

import streamlit as st
from utils.sheets_manager import SheetsManager
from utils.styles import MAIN_CSS, FOOTER_HTML

# ページ設定
st.set_page_config(
    page_title="債権者データ管理システム",
    layout="wide"
)

# CSS適用
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# Google Sheets Manager初期化
@st.cache_resource
def get_sheets_manager():
    return SheetsManager()

def main():
    """ホームページ"""
    
    # タイトル
    st.title("債権者データ管理システム")
    st.markdown("Google Sheets連携による効率的な債権者情報管理")
    
    # 接続状態表示
    sheets_manager = get_sheets_manager()
    
    if sheets_manager.is_connected():
        st.markdown('<span class="status-badge status-connected">Google Sheets 接続中</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-error">接続エラー</span>', unsafe_allow_html=True)
        st.error("Google Sheetsに接続できません。credentials.jsonファイルまたはSecrets設定を確認してください。")
    

    
    # フッター
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

if __name__ == "__main__":
    main()