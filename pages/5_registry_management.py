import streamlit as st
import sys
import os
import json
from datetime import datetime

# パス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.template_manager import TemplateManager
from utils.styles import MAIN_CSS

# CSS適用
st.markdown(MAIN_CSS, unsafe_allow_html=True)

st.title("テンプレートレジストリ管理")

# セッション状態の初期化
if 'last_operation' not in st.session_state:
    st.session_state.last_operation = None
if 'operation_result' not in st.session_state:
    st.session_state.operation_result = None

def get_template_manager():
    """Template Managerを取得（キャッシュなし）"""
    try:
        return TemplateManager()
    except Exception as e:
        st.error(f"TemplateManager初期化エラー: {e}")
        return None

def safe_operation(operation_name, operation_func):
    """安全に操作を実行"""
    try:
        with st.spinner(f"{operation_name}中..."):
            result = operation_func()
            st.session_state.last_operation = operation_name
            st.session_state.operation_result = "success"
            return result
    except Exception as e:
        st.error(f"{operation_name}エラー: {str(e)}")
        st.session_state.last_operation = operation_name
        st.session_state.operation_result = "error"
        return None

def display_registry_info():
    """レジストリ情報を表示"""
    template_manager = get_template_manager()
    if not template_manager:
        return
    
    try:
        # 基本統計
        registry = template_manager.load_registry()
        if not registry:
            st.info("レジストリが空です")
            return
        
        # 統計計算
        total_courts = len(registry)
        total_templates = 0
        court_details = []
        
        for court_name, court_data in registry.items():
            procedures = []
            for key, value in court_data.items():
                if isinstance(value, dict) and "債権者一覧表" in value:
                    if key in ["個人再生", "自己破産"]:
                        procedures.append(key)
                        total_templates += 1
            
            court_details.append({
                "name": court_name,
                "procedures": procedures,
                "count": len(procedures)
            })
        
        # メトリクス表示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("登録裁判所数", total_courts)
        with col2:
            st.metric("総テンプレート数", total_templates)
        with col3:
            available_count = sum(1 for court in court_details if court["count"] > 0)
            st.metric("テンプレート保有裁判所", available_count)
        
        # 詳細表示
        st.markdown("---")
        st.subheader("裁判所別テンプレート詳細")
        
        if court_details:
            for court in court_details:
                if court["count"] > 0:
                    with st.expander(f"{court['name']} - {court['count']}件"):
                        for procedure in court['procedures']:
                            template_key = f"{court['name']}_{procedure}"
                            template_info = template_manager.get_template_info(template_key)
                            
                            if template_info:
                                st.markdown(f"**{procedure}**")
                                info_col1, info_col2 = st.columns(2)
                                with info_col1:
                                    st.text(f"説明: {template_info.get('description', 'なし')}")
                                    st.text(f"作成日: {template_info.get('created_date', 'なし')}")
                                with info_col2:
                                    st.text(f"最終更新: {template_info.get('last_modified', 'なし')}")
                                    file_path = template_info.get('file_path', '')
                                    exists = os.path.exists(file_path) if file_path else False
                                    st.text(f"ファイル: {'存在' if exists else '不存在'}")
                                st.markdown("---")
        else:
            st.info("登録されているテンプレートはありません")
    
    except Exception as e:
        st.error(f"レジストリ情報取得エラー: {str(e)}")

def display_registry_operations():
    """レジストリ操作を表示"""
    template_manager = get_template_manager()
    if not template_manager:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**レジストリリセット**")
        st.write("レジストリファイルを完全に削除して初期化します")
        st.warning("注意: この操作は元に戻すことができません")
        
        if st.button("レジストリをリセット", type="secondary", key="reset_btn"):
            if st.session_state.get('confirm_reset', False):
                def reset_operation():
                    return template_manager.reset_registry()
                
                result = safe_operation("レジストリリセット", reset_operation)
                if result:
                    st.success("レジストリをリセットしました")
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("もう一度クリックすると実行されます")
    
    with col2:
        st.markdown("**レジストリ再構築**")
        st.write("ファイルシステムを走査してレジストリを再構築します")
        
        if st.button("レジストリを再構築", type="primary", key="rebuild_btn"):
            def rebuild_operation():
                return template_manager.rebuild_registry()
            
            result = safe_operation("レジストリ再構築", rebuild_operation)
            if result:
                st.success("レジストリを再構築しました")
                st.rerun()

def display_maintenance():
    """メンテナンス機能を表示"""
    template_manager = get_template_manager()
    if not template_manager:
        return
    
    st.markdown("**レジストリ内容の直接確認**")
    if st.checkbox("レジストリファイルの内容を表示", key="show_registry"):
        try:
            registry = template_manager.load_registry()
            if registry:
                st.json(registry)
            else:
                st.info("レジストリが空です")
        except Exception as e:
            st.error(f"レジストリ読み込みエラー: {str(e)}")
    
    st.markdown("---")
    
    st.markdown("**空ディレクトリのクリーンアップ**")
    st.write("使用されていない裁判所ディレクトリを確認できます")
    
    # 空ディレクトリの確認
    empty_dirs = []
    if os.path.exists("templates"):
        for item in os.listdir("templates"):
            item_path = os.path.join("templates", item)
            if os.path.isdir(item_path) and item != "template_registry.json":
                # ディレクトリ内にテンプレートファイルがあるかチェック
                has_templates = False
                for root, dirs, files in os.walk(item_path):
                    if "債権者一覧表.xlsx" in files:
                        has_templates = True
                        break
                
                if not has_templates:
                    empty_dirs.append(item)
    
    if empty_dirs:
        st.info(f"テンプレートが登録されていない裁判所: {len(empty_dirs)}件")
        for empty_dir in empty_dirs:
            st.text(f"- {empty_dir}")
    else:
        st.success("すべての裁判所ディレクトリが使用されています")

def display_backup():
    """バックアップ管理を表示"""
    template_manager = get_template_manager()
    if not template_manager:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**バックアップ作成**")
        if st.button("現在のレジストリをバックアップ", type="primary", key="backup_btn"):
            def backup_operation():
                return template_manager.backup_registry()
            
            backup_file = safe_operation("バックアップ作成", backup_operation)
            if backup_file:
                st.success("バックアップを作成しました")
                st.code(os.path.basename(backup_file))
    
    with col2:
        st.markdown("**バックアップファイル一覧**")
        try:
            template_dir = template_manager.base_path
            backup_files = []
            
            if os.path.exists(template_dir):
                for file in os.listdir(template_dir):
                    if file.startswith("template_registry.json.backup_"):
                        file_path = os.path.join(template_dir, file)
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        backup_files.append({
                            "name": file,
                            "time": mod_time
                        })
            
            if backup_files:
                backup_files.sort(key=lambda x: x["time"], reverse=True)
                st.write("最新5件のバックアップ:")
                for backup in backup_files[:5]:
                    st.text(f"{backup['name']}")
                    st.caption(f"作成日時: {backup['time'].strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.info("バックアップファイルはありません")
        
        except Exception as e:
            st.error(f"バックアップファイル一覧取得エラー: {str(e)}")

# メインコンテンツ
tab1, tab2, tab3, tab4 = st.tabs(["レジストリ情報", "レジストリ操作", "メンテナンス", "バックアップ"])

with tab1:
    st.subheader("現在のレジストリ情報")
    display_registry_info()

with tab2:
    st.subheader("レジストリ操作")
    display_registry_operations()

with tab3:
    st.subheader("メンテナンス機能")
    display_maintenance()

with tab4:
    st.subheader("バックアップ管理")
    display_backup()

# 操作結果の表示
if st.session_state.last_operation and st.session_state.operation_result:
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

# 使用方法
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
