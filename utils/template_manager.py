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
        
        procedure_types = ["個人再生", "自己破産"]
        
        # ベースディレクトリ作成
        os.makedirs(self.base_path, exist_ok=True)
        
        # 各裁判所のディレクトリ作成
        for court in courts:
            court_path = os.path.join(self.base_path, court)
            os.makedirs(court_path, exist_ok=True)
            
            # 各手続種別のサブディレクトリ作成
            for procedure in procedure_types:
                procedure_path = os.path.join(court_path, procedure)
                os.makedirs(procedure_path, exist_ok=True)
        
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
    
    def parse_template_key(self, template_key):
        """テンプレートキーを解析して裁判所名と手続種別を抽出"""
        parts = template_key.rsplit('_', 1)
        return parts[0], parts[1]
    
    def create_template_key(self, court_name, procedure_type):
        """裁判所名と手続種別からテンプレートキーを生成"""
        return f"{court_name}_{procedure_type}"
    
    def save_template(self, template_key, file_data, description="債権者一覧表", file_extension=".xlsx"):
        """テンプレートを保存（Word/Excel対応）"""
        try:
            court_name, procedure_type = self.parse_template_key(template_key)
            
            # ファイル名を拡張子に応じて決定
            if file_extension == ".docx":
                filename = "債権者一覧表.docx"
            else:
                filename = "債権者一覧表.xlsx"
            
            # ファイルパス生成
            court_path = os.path.join(self.base_path, court_name)
            procedure_path = os.path.join(court_path, procedure_type)
            file_path = os.path.join(procedure_path, filename)
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(procedure_path, exist_ok=True)
            
            # 既存の異なる形式のファイルを削除
            for ext in [".xlsx", ".docx"]:
                if ext != file_extension:
                    old_file = os.path.join(procedure_path, f"債権者一覧表{ext}")
                    if os.path.exists(old_file):
                        os.remove(old_file)
            
            # ファイル保存
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # レジストリ更新
            self.update_registry(court_name, procedure_type, file_path, description)
            
            return True
            
        except Exception as e:
            st.error(f"テンプレート保存エラー: {e}")
            return False
    
    def update_registry(self, court_name, procedure_type, file_path, description):
        """レジストリを更新"""
        try:
            registry = self.load_registry()
            
            if court_name not in registry:
                registry[court_name] = {}
            
            if procedure_type not in registry[court_name]:
                registry[court_name][procedure_type] = {}
            
            registry[court_name][procedure_type]["債権者一覧表"] = {
                "file_path": file_path,
                "description": description,
                "created_date": datetime.now().strftime('%Y-%m-%d'),
                "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # レジストリファイルに書き込み
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            return True
                
        except Exception as e:
            st.error(f"レジストリ更新エラー: {e}")
            return False
    
    def get_template_path(self, template_key):
        """指定されたテンプレートキーのテンプレートパスを取得（Word/Excel対応）"""
        court_name, procedure_type = self.parse_template_key(template_key)
        
        # まずレジストリから確認
        registry = self.load_registry()
        if (court_name in registry and 
            procedure_type in registry[court_name] and
            "債権者一覧表" in registry[court_name][procedure_type]):
            registered_path = registry[court_name][procedure_type]["債権者一覧表"]["file_path"]
            if os.path.exists(registered_path):
                return registered_path
        
        # レジストリにない場合はファイルシステムから検索
        for extension in [".docx", ".xlsx"]:
            filename = f"債権者一覧表{extension}"
            file_path = os.path.join(self.base_path, court_name, procedure_type, filename)
            if os.path.exists(file_path):
                return file_path
        
        return None
    
    def template_exists(self, template_key):
        """テンプレートの存在確認"""
        return self.get_template_path(template_key) is not None
    
    def list_available_templates(self):
        """利用可能なテンプレート一覧を取得"""
        registry = self.load_registry()
        available_templates = []
        
        for court_name in registry.keys():
            for procedure_type in registry[court_name].keys():
                if "債権者一覧表" in registry[court_name][procedure_type]:
                    template_key = self.create_template_key(court_name, procedure_type)
                    # ファイルの実在確認
                    if self.template_exists(template_key):
                        available_templates.append({
                            "template_key": template_key,
                            "court_name": court_name,
                            "procedure_type": procedure_type
                        })
        
        return available_templates
    
    def list_available_courts(self):
        """テンプレートが登録されている裁判所一覧を取得"""
        templates = self.list_available_templates()
        courts = list(set([t["court_name"] for t in templates]))
        return courts
    
    def get_template_info(self, template_key):
        """テンプレート情報を取得"""
        court_name, procedure_type = self.parse_template_key(template_key)
        registry = self.load_registry()
        
        if (court_name in registry and 
            procedure_type in registry[court_name] and
            "債権者一覧表" in registry[court_name][procedure_type]):
            info = registry[court_name][procedure_type]["債権者一覧表"]
            
            # ファイルの実在確認を追加
            file_path = info.get("file_path", "")
            if file_path and os.path.exists(file_path):
                info["file_exists"] = True
                info["file_size"] = os.path.getsize(file_path)
            else:
                info["file_exists"] = False
                info["file_size"] = 0
            
            return info
        
        return None
    
    def delete_template(self, template_key):
        """テンプレートを削除"""
        try:
            court_name, procedure_type = self.parse_template_key(template_key)
            
            # ファイル削除（Word/Excel両方チェック）
            deleted_files = []
            for extension in [".xlsx", ".docx"]:
                filename = f"債権者一覧表{extension}"
                file_path = os.path.join(self.base_path, court_name, procedure_type, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(filename)
            
            # レジストリから削除
            registry = self.load_registry()
            
            if (court_name in registry and 
                procedure_type in registry[court_name] and
                "債権者一覧表" in registry[court_name][procedure_type]):
                del registry[court_name][procedure_type]["債権者一覧表"]
                
                # 手続種別のエントリが空になった場合は削除
                if not registry[court_name][procedure_type]:
                    del registry[court_name][procedure_type]
                
                # 裁判所のエントリが空になった場合は削除
                if not registry[court_name]:
                    del registry[court_name]
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            if deleted_files:
                st.success(f"削除されたファイル: {', '.join(deleted_files)}")
            
            return True
            
        except Exception as e:
            st.error(f"テンプレート削除エラー: {e}")
            return False
    
    def reset_registry(self):
        """レジストリを完全にリセット"""
        try:
            if os.path.exists(self.registry_file):
                os.remove(self.registry_file)
            self.init_registry()
            return True
        except Exception as e:
            st.error(f"レジストリリセットエラー: {e}")
            return False
    
    def rebuild_registry(self):
        """ファイルシステムからレジストリを再構築（Word/Excel対応）"""
        try:
            new_registry = {}
            
            # templatesディレクトリを走査
            if os.path.exists(self.base_path):
                for court_item in os.listdir(self.base_path):
                    court_path = os.path.join(self.base_path, court_item)
                    
                    if os.path.isdir(court_path) and court_item != "template_registry.json":
                        court_name = court_item
                        
                        # 手続種別フォルダをチェック
                        for procedure_item in os.listdir(court_path):
                            procedure_path = os.path.join(court_path, procedure_item)
                            
                            if os.path.isdir(procedure_path) and procedure_item in ["個人再生", "自己破産"]:
                                # Word/Excelファイルをチェック
                                template_file = None
                                for extension in [".docx", ".xlsx"]:
                                    test_file = os.path.join(procedure_path, f"債権者一覧表{extension}")
                                    if os.path.exists(test_file):
                                        template_file = test_file
                                        break
                                
                                if template_file:
                                    if court_name not in new_registry:
                                        new_registry[court_name] = {}
                                    if procedure_item not in new_registry[court_name]:
                                        new_registry[court_name][procedure_item] = {}
                                    
                                    # ファイルの更新日時を取得
                                    mod_time = datetime.fromtimestamp(os.path.getmtime(template_file))
                                    
                                    new_registry[court_name][procedure_item]["債権者一覧表"] = {
                                        "file_path": template_file,
                                        "description": f"{procedure_item}用債権者一覧表",
                                        "created_date": mod_time.strftime('%Y-%m-%d'),
                                        "last_modified": mod_time.strftime('%Y-%m-%d %H:%M:%S')
                                    }
            
            # 新しいレジストリを保存
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(new_registry, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"レジストリ再構築エラー: {e}")
            return False
    
    def backup_registry(self):
        """レジストリのバックアップを作成"""
        try:
            if os.path.exists(self.registry_file):
                backup_file = f"{self.registry_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                import shutil
                shutil.copy2(self.registry_file, backup_file)
                return backup_file
            else:
                st.warning("バックアップするレジストリファイルが見つかりません")
                return None
        except Exception as e:
            st.error(f"バックアップエラー: {e}")
            return None
    
    def get_registry_info(self):
        """レジストリの詳細情報を取得"""
        registry = self.load_registry()
        info = {
            "total_courts": len(registry),
            "total_templates": 0,
            "courts": []
        }
        
        for court_name, court_data in registry.items():
            court_info = {
                "name": court_name,
                "procedures": []
            }
            
            for key, value in court_data.items():
                if isinstance(value, dict) and "債権者一覧表" in value:
                    if key in ["個人再生", "自己破産"]:
                        court_info["procedures"].append(key)
                        info["total_templates"] += 1
            
            info["courts"].append(court_info)
        
        return info

    def list_templates(self):
        """登録済みテンプレート一覧を取得"""
        templates = []
        registry = self.load_registry()
        
        for court_name in registry.keys():
            for procedure_type in registry[court_name].keys():
                if "債権者一覧表" in registry[court_name][procedure_type]:
                    template_key = self.create_template_key(court_name, procedure_type)
                    template_info = registry[court_name][procedure_type]["債権者一覧表"].copy()
                    
                    # 追加情報を設定
                    template_info['key'] = template_key
                    template_info['court'] = court_name
                    template_info['procedure_type'] = procedure_type
                    
                    # ファイル拡張子を取得
                    template_path = self.get_template_path(template_key)
                    if template_path:
                        template_info['file_extension'] = os.path.splitext(template_path)[1]
                    else:
                        template_info['file_extension'] = '.xlsx'
                    
                    templates.append(template_info)
        
        # 裁判所名でソート
        templates.sort(key=lambda x: x['court'])
        return templates