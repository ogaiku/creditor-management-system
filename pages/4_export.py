import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 既存のユーティリティをインポート
from utils.sheets_manager import SheetsManager
from utils.template_manager import TemplateManager
from utils.styles import MAIN_CSS, get_success_html, get_warning_html

# 新しく分割したモジュールをインポート
from utils.data_handler import DataHandler
from utils.template_processor import TemplateProcessor
from utils.constants import COURTS, PROCEDURE_TYPES, TEMPLATE_VARIABLES

st.title("エクスポート機能")

# テンプレート管理タブ
tab1, tab2 = st.tabs(["テンプレート使用", "テンプレート登録"])

try:
    # CSS適用
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    
    @st.cache_resource
    def get_managers():
        return SheetsManager(), TemplateManager()
    
    sheets_manager, template_manager = get_managers()
    
    if not sheets_manager.is_connected():
        st.error("Google Sheets接続エラー")
        st.stop()
    
    # データハンドラーとテンプレートプロセッサーの初期化
    data_handler = DataHandler(sheets_manager)
    template_processor = TemplateProcessor(template_manager)
    
    # テンプレート使用タブ
    with tab1:
        from components.template_usage_tab import render_template_usage_tab
        render_template_usage_tab(
            data_handler, 
            template_processor, 
            sheets_manager, 
            template_manager
        )
    
    # テンプレート登録タブ
    with tab2:
        from components.template_registration_tab import render_template_registration_tab
        render_template_registration_tab(template_manager)
    
    # 使用方法説明
    from components.help_section import render_help_section
    render_help_section()
       
except Exception as e:
    st.error(f"エクスポート機能の初期化エラー: {e}")
    st.write("詳細なエラー情報:")
    import traceback
    st.text(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("トラブルシューティング")
    st.write("1. Google Sheetsの認証情報が正しく設定されているか確認")
    st.write("2. utils/ディレクトリのファイルが正常に読み込めるか確認")
    st.write("3. 必要なライブラリがインストールされているか確認")