import streamlit as st
import sys
import os

# パス設定 - creditor_managementディレクトリを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
creditor_management_dir = os.path.join(current_dir, 'creditor_management')
sys.path.insert(0, creditor_management_dir)

# 作業ディレクトリを変更（ファイルが存在する場合のみ）
if os.path.exists(creditor_management_dir):
    os.chdir(creditor_management_dir)

# 設定の直接定義（importエラーを回避）
APP_CONFIG = {
    "title": "債権者データ管理システム",
    "version": "2.1",
    "description": "Google Sheets連携による効率的な債権者情報管理",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

STATUS_OPTIONS = ["未処理", "確認中", "処理済み", "保留中", "完了"]

# 基本的なスタイル定義
MAIN_CSS = """
<style>
    .main {
        background-color: #ffffff;
        padding: 1rem;
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
"""

FOOTER_HTML = """
<div style="text-align: center; color: #6c757d; padding: 1.5rem; background-color: #f8f9fa; border-top: 1px solid #e8e8e8; margin-top: 2rem;">
    <div style="margin-bottom: 0.8rem;">
        <strong style="color: #495057;">債権者データ管理システム</strong><br>
        効率的な債権者情報管理
    </div>
    <div style="border-top: 1px solid #e0e0e0; padding-top: 0.8rem; font-size: 0.8rem;">
        © 2025 <strong>Mamori Law Firm</strong>. All rights reserved.
    </div>
</div>
"""

# ページ設定
st.set_page_config(
    page_title=APP_CONFIG["title"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"]
)

# CSS適用
st.markdown(MAIN_CSS, unsafe_allow_html=True)

def main():
    """ホームページ"""
    
    # タイトル
    st.title(APP_CONFIG["title"])
    st.markdown(APP_CONFIG["description"])
    
    # 接続状態表示
    try:
        # creditor_managementディレクトリからインポートを試行
        if os.path.exists(creditor_management_dir):
            sys.path.insert(0, creditor_management_dir)
        
        from utils.sheets_manager import SheetsManager
        
        @st.cache_resource
        def get_sheets_manager():
            try:
                return SheetsManager()
            except Exception as e:
                st.error(f"SheetsManager初期化エラー: {e}")
                return None
        
        sheets_manager = get_sheets_manager()
        
        if sheets_manager and sheets_manager.is_connected():
            st.markdown('<span class="status-badge status-connected">Google Sheets 接続中</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-error">接続エラー</span>', unsafe_allow_html=True)
            if 'gcp_service_account' in st.secrets:
                st.error("Google Sheets認証に失敗しました。Secrets設定を確認してください。")
            else:
                st.error("Google Sheets認証情報が設定されていません。")
    except Exception as e:
        st.error(f"システム初期化エラー: {e}")
        st.info("左のメニューから各機能をご利用ください。")
    
    # 使用方法
    st.markdown("---")
    st.subheader("使用方法")
    st.markdown("""
    1. **左のメニューから機能を選択**してください
    2. **JSON一括取り込み**: ClaimExtract-GPTで抽出したJSONデータを貼り付け
    3. **手動データ登録**: 個別にデータを入力
    4. **スプレッドシート一覧**: 作成されたデータを確認・編集
    """)
    
    # フッター
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)

if __name__ == "__main__":
    main()