import os
import json
from datetime import datetime
import streamlit as st

class TemplateManager:
    def __init__(self):
        self.base_path = "templates"
        self.registry_file = "templates/template_registry.json"
        self.ensure_directories()
    
    def ensure_directories(self):
        """必要なディレクトリを作成"""
        courts = [
            "東京地方裁判所",
            "大阪地方裁判所", 
            "名古屋地方裁判所",
            "横浜地方裁判所",
            "神戸地方裁判所",
            "福岡地方裁判所",
            "仙台地方裁判所",
            "広島地方裁判所",
            "札幌地方裁判所",
            "その他"
        ]
        
        # ベースディレクトリ作成
        os.makedirs(self.base_path, exist_ok=True)
        
        # 各裁判所のディレクトリ作成
        for court in courts:
            court_path = os.path.join(self.base_path, court)
            os.makedirs(court_path, exist_ok=True)
        
        # レジストリファイルの初期化
        if not os.path.exists(self.registry_file):
            self.init_registry()
    
    def init_registry(self):
        """テンプレートレジストリファイルを初期化"""
        initial_registry = {}
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(initial_registry, f, ensure_ascii=False, indent=2)
    
    def load_registry(self):
        """レジストリファイルを読み込み"""
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.init_registry()
            return {}
    
    def save_template(self, court_name, file_data, description="債権者一覧表"):
        """テンプレートを保存"""
        try:
            # ファイルパス生成
            court_path = os.path.join(self.base_path, court_name)
            file_path = os.path.join(court_path, "債権者一覧表.xlsx")
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # レジストリ更新
            self.update_registry(court_name, file_path, description)
            return True
            
        except Exception as e:
            st.error(f"テンプレート保存エラー: {e}")
            return False
    
    def update_registry(self, court_name, file_path, description):
        """レジストリを更新"""
        registry = self.load_registry()
        
        if court_name not in registry:
            registry[court_name] = {}
        
        registry[court_name]["債権者一覧表"] = {
            "file_path": file_path,
            "description": description,
            "created_date": datetime.now().strftime('%Y-%m-%d'),
            "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def get_template_path(self, court_name):
        """指定された裁判所のテンプレートパスを取得"""
        file_path = os.path.join(self.base_path, court_name, "債権者一覧表.xlsx")
        return file_path if os.path.exists(file_path) else None
    
    def template_exists(self, court_name):
        """テンプレートの存在確認"""
        return self.get_template_path(court_name) is not None
    
    def list_available_courts(self):
        """テンプレートが登録されている裁判所一覧を取得"""
        registry = self.load_registry()
        available_courts = []
        
        for court_name in registry.keys():
            if "債権者一覧表" in registry[court_name]:
                available_courts.append(court_name)
        
        return available_courts
    
    def get_template_info(self, court_name):
        """テンプレート情報を取得"""
        registry = self.load_registry()
        
        if court_name in registry and "債権者一覧表" in registry[court_name]:
            return registry[court_name]["債権者一覧表"]
        
        return None
    
    def delete_template(self, court_name):
        """テンプレートを削除"""
        try:
            # ファイル削除
            file_path = self.get_template_path(court_name)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # レジストリから削除
            registry = self.load_registry()
            if court_name in registry and "債権者一覧表" in registry[court_name]:
                del registry[court_name]["債権者一覧表"]
                
                # 裁判所のエントリが空になった場合は削除
                if not registry[court_name]:
                    del registry[court_name]
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"テンプレート削除エラー: {e}")