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
        if '_' in template_key:
            parts = template_key.rsplit('_', 1)  # 右から最初の_で分割
            return parts[0], parts[1]  # court_name, procedure_type
        else:
            # 後方互換性のため、従来形式もサポート
            return template_key, "債権者一覧表"
    
    def create_template_key(self, court_name, procedure_type):
        """裁判所名と手続種別からテンプレートキーを生成"""
        return f"{court_name}_{procedure_type}"
    
    def save_template(self, template_key, file_data, description="債権者一覧表"):
        """テンプレートを保存（template_keyは裁判所_手続種別の形式）"""
        try:
            court_name, procedure_type = self.parse_template_key(template_key)
            
            # ファイルパス生成
            court_path = os.path.join(self.base_path, court_name)
            procedure_path = os.path.join(court_path, procedure_type)
            file_path = os.path.join(procedure_path, "債権者一覧表.xlsx")
            
            # ディレクトリが存在しない場合は作成
            os.makedirs(procedure_path, exist_ok=True)
            
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
        
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
    
    def get_template_path(self, template_key):
        """指定されたテンプレートキーのテンプレートパスを取得"""
        court_name, procedure_type = self.parse_template_key(template_key)
        
        # 新形式のパスを試行
        file_path = os.path.join(self.base_path, court_name, procedure_type, "債権者一覧表.xlsx")
        if os.path.exists(file_path):
            return file_path
        
        # 後方互換性：従来形式のパスも試行
        old_file_path = os.path.join(self.base_path, court_name, "債権者一覧表.xlsx")
        if os.path.exists(old_file_path):
            return old_file_path
        
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
                    available_templates.append({
                        "template_key": template_key,
                        "court_name": court_name,
                        "procedure_type": procedure_type
                    })
        
        return available_templates
    
    def list_available_courts(self):
        """テンプレートが登録されている裁判所一覧を取得（後方互換性）"""
        templates = self.list_available_templates()
        courts = list(set([t["court_name"] for t in templates]))
        return courts
    
    def get_template_info(self, template_key):
        """テンプレート情報を取得"""
        court_name, procedure_type = self.parse_template_key(template_key)
        registry = self.load_registry()
        
        # 新形式で検索
        if (court_name in registry and 
            procedure_type in registry[court_name] and
            "債権者一覧表" in registry[court_name][procedure_type]):
            return registry[court_name][procedure_type]["債権者一覧表"]
        
        # 後方互換性：従来形式で検索
        if (court_name in registry and 
            "債権者一覧表" in registry[court_name] and
            isinstance(registry[court_name]["債権者一覧表"], dict)):
            return registry[court_name]["債権者一覧表"]
        
        return None
    
    def delete_template(self, template_key):
        """テンプレートを削除"""
        try:
            court_name, procedure_type = self.parse_template_key(template_key)
            
            # ファイル削除
            file_path = self.get_template_path(template_key)
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # レジストリから削除
            registry = self.load_registry()
            
            # 新形式の削除
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
            
            # 後方互換性：従来形式の削除
            elif (court_name in registry and 
                  "債権者一覧表" in registry[court_name]):
                del registry[court_name]["債権者一覧表"]
                
                if not registry[court_name]:
                    del registry[court_name]
            
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"テンプレート削除エラー: {e}")
            return False
    
    def migrate_old_templates(self):
        """従来形式のテンプレートを新形式に移行"""
        registry = self.load_registry()
        migrated = False
        
        for court_name in list(registry.keys()):
            # 従来形式のテンプレートが存在する場合
            if ("債権者一覧表" in registry[court_name] and 
                isinstance(registry[court_name]["債権者一覧表"], dict)):
                
                old_template_info = registry[court_name]["債権者一覧表"]
                old_file_path = old_template_info.get("file_path")
                
                if old_file_path and os.path.exists(old_file_path):
                    # 個人再生と自己破産の両方にコピー
                    for procedure_type in ["個人再生", "自己破産"]:
                        new_procedure_path = os.path.join(self.base_path, court_name, procedure_type)
                        os.makedirs(new_procedure_path, exist_ok=True)
                        
                        new_file_path = os.path.join(new_procedure_path, "債権者一覧表.xlsx")
                        
                        # ファイルをコピー
                        import shutil
                        shutil.copy2(old_file_path, new_file_path)
                        
                        # 新形式でレジストリに登録
                        if court_name not in registry:
                            registry[court_name] = {}
                        if procedure_type not in registry[court_name]:
                            registry[court_name][procedure_type] = {}
                        
                        registry[court_name][procedure_type]["債権者一覧表"] = {
                            "file_path": new_file_path,
                            "description": old_template_info.get("description", "債権者一覧表"),
                            "created_date": old_template_info.get("created_date", datetime.now().strftime('%Y-%m-%d')),
                            "last_modified": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        migrated = True
                
                # 従来形式のエントリを削除
                if "債権者一覧表" in registry[court_name]:
                    del registry[court_name]["債権者一覧表"]
        
        if migrated:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            st.info("既存のテンプレートを新形式に移行しました")
        
        return migrated
    
    def reset_registry(self):
        """レジストリを完全にリセット"""
        try:
            if os.path.exists(self.registry_file):
                os.remove(self.registry_file)
            self.init_registry()
            st.success("テンプレートレジストリをリセットしました")
            return True
        except Exception as e:
            st.error(f"レジストリリセットエラー: {e}")
            return False
    
    def rebuild_registry(self):
        """ファイルシステムからレジストリを再構築"""
        try:
            new_registry = {}
            
            # templatesディレクトリを走査
            if os.path.exists(self.base_path):
                for court_item in os.listdir(self.base_path):
                    court_path = os.path.join(self.base_path, court_item)
                    
                    if os.path.isdir(court_path) and court_item != "template_registry.json":
                        court_name = court_item
                        
                        # 新形式：手続種別フォルダがある場合
                        has_procedure_folders = False
                        for procedure_item in os.listdir(court_path):
                            procedure_path = os.path.join(court_path, procedure_item)
                            
                            if os.path.isdir(procedure_path) and procedure_item in ["個人再生", "自己破産"]:
                                has_procedure_folders = True
                                template_file = os.path.join(procedure_path, "債権者一覧表.xlsx")
                                
                                if os.path.exists(template_file):
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
                        
                        # 従来形式：直接テンプレートファイルがある場合
                        if not has_procedure_folders:
                            template_file = os.path.join(court_path, "債権者一覧表.xlsx")
                            if os.path.exists(template_file):
                                if court_name not in new_registry:
                                    new_registry[court_name] = {}
                                
                                mod_time = datetime.fromtimestamp(os.path.getmtime(template_file))
                                
                                new_registry[court_name]["債権者一覧表"] = {
                                    "file_path": template_file,
                                    "description": "債権者一覧表",
                                    "created_date": mod_time.strftime('%Y-%m-%d'),
                                    "last_modified": mod_time.strftime('%Y-%m-%d %H:%M:%S')
                                }
            
            # 新しいレジストリを保存
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(new_registry, f, ensure_ascii=False, indent=2)
            
            st.success("ファイルシステムからレジストリを再構築しました")
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
                st.success(f"レジストリをバックアップしました: {backup_file}")
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
                    # 新形式
                    if key in ["個人再生", "自己破産"]:
                        court_info["procedures"].append(key)
                        info["total_templates"] += 1
                    # 従来形式
                    elif key == "債権者一覧表":
                        court_info["procedures"].append("従来形式")
                        info["total_templates"] += 1
            
            info["courts"].append(court_info)
        
        return info
