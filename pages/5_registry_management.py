import streamlit as st
import sys
import os

# パス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.template_manager import TemplateManager
from utils.registry_utils import RegistryUtils
from utils.styles import MAIN_CSS

# 分割されたコンポーネントをインポート
from components.registry_info_tab import render_registry_info_tab
from components.registry_operations_tab import render_registry_operations_tab
from components.maintenance_tab import render_maintenance_tab
from components.backup_tab import render_backup_tab

# CSS適用
st.markdown(MAIN_CSS, unsafe_allow_html=True)

st.title("テンプレートレジストリ管理")

def get_template_manager():
    """Template Managerを取得"""
    try:
        return TemplateManager()
    except Exception as e:
        st.error(f"TemplateManager初期化エラー: {e}")
        return None

def render_operation_result():
    """操作結果を表示"""
    if st.session_state.get('last_operation') and st.session_state.get('operation_result'):
        st.markdown("---")
        
        if st.session_state.operation_result == "success":
            st.success(f"前回の操作「{st.session_state.last_operation}」が正常に完了しました")
        elif st.session_state.operation_result == "error":
            st.error(f"前回の操作「{st.session_state.last_operation}」でエラーが発生しました")
        
        # 結果をクリア
        if st.button("メッセージをクリア", type="secondary"):
            st.session_state.last_operation = None
            st.session_state.operation_result = None
            st.rerun()

def render_help_section():
    """ヘルプセクションをレンダリング"""
    st.markdown("---")
    st.subheader("使用方法")
    
    usage_col1, usage_col2 = st.columns(2)
    
    with usage_col1:
        st.markdown("**基本的な手順:**")
        st.markdown("""
        1. レジストリ情報で現在の状態を確認
        2. 問題がある場合はレジストリ再構築を実行
        3. 重要な変更前にバックアップを作成
        4. メンテナンス機能で空ディレクトリを確認
        """)
    
    with usage_col2:
        st.markdown("**トラブルシューティング:**")
        st.markdown("""
        - テンプレートが表示されない → レジストリ再構築
        - レジストリが破損した → バックアップから復元
        - 操作が失敗する → エラーメッセージを確認
        - 不要なディレクトリがある → メンテナンスで確認
        """)

# メイン処理
try:
    # Template Managerを取得
    template_manager = get_template_manager()
    if not template_manager:
        st.stop()
    
    # Registry Utilsを初期化
    registry_utils = RegistryUtils(template_manager)
    registry_utils.initialize_session_state()
    
    # タブを作成
    tab1, tab2, tab3, tab4 = st.tabs([
        "レジストリ情報", 
        "レジストリ操作", 
        "メンテナンス", 
        "バックアップ"
    ])
    
    # 各タブの内容をレンダリング
    with tab1:
        render_registry_info_tab(registry_utils)
    
    with tab2:
        render_registry_operations_tab(registry_utils)
    
    with tab3:
        render_maintenance_tab(registry_utils)
    
    with tab4:
        render_backup_tab(registry_utils)
    
    # 操作結果の表示
    render_operation_result()
    
    # ヘルプセクション
    render_help_section()

except Exception as e:
    st.error(f"アプリケーション初期化エラー: {e}")
    st.write("詳細なエラー情報:")
    import traceback
    st.text(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("トラブルシューティング")
    st.write("1. Template Managerが正しく初期化されているか確認")
    st.write("2. 必要なディレクトリが存在するか確認")
    st.write("3. ファイルの読み書き権限を確認")