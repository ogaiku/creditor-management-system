import streamlit as st
import os
from datetime import datetime

class RegistryUtils:
    def __init__(self, template_manager):
        self.template_manager = template_manager
    
    def safe_operation(self, operation_name, operation_func):
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
    
    def get_registry_statistics(self):
        """レジストリ統計を取得"""
        try:
            registry = self.template_manager.load_registry()
            if not registry:
                return None, None, []
            
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
            
            return total_courts, total_templates, court_details
            
        except Exception as e:
            st.error(f"統計取得エラー: {str(e)}")
            return None, None, []
    
    def get_empty_directories(self):
        """空のディレクトリを取得"""
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
        
        return empty_dirs
    
    def get_backup_files(self):
        """バックアップファイル一覧を取得"""
        try:
            template_dir = self.template_manager.base_path
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
            
            backup_files.sort(key=lambda x: x["time"], reverse=True)
            return backup_files
            
        except Exception as e:
            st.error(f"バックアップファイル一覧取得エラー: {str(e)}")
            return []
    
    def initialize_session_state(self):
        """セッション状態を初期化"""
        if 'last_operation' not in st.session_state:
            st.session_state.last_operation = None
        if 'operation_result' not in st.session_state:
            st.session_state.operation_result = None
        if 'confirm_reset' not in st.session_state:
            st.session_state.confirm_reset = False