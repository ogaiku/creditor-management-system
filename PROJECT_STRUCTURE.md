# 債権者管理システム - プロジェクト構造

## メインファイル
- `main.py` - アプリケーションのエントリーポイント

## 設定ファイル
- `config/`
  - `settings.py` - アプリケーション設定
  - `__init__.py` - パッケージ初期化

## ページファイル (`pages/`)
- `1_json_import.py` - JSONファイルからのデータインポート
- `2_manual_input.py` - 手動データ入力
- `3_spreadsheet_list.py` - スプレッドシート一覧表示
- `4_export.py` - 債権者一覧表エクスポート機能
- `5_registry_management.py` - レジストリ管理
- `__init__.py` - パッケージ初期化

## ユーティリティ (`utils/`)
- `sheets_manager.py` - Google Sheets操作管理
- `template_manager.py` - テンプレート管理
- `styles.py` - CSS スタイル定義
- `data_processor.py` - データ処理ユーティリティ
- `__init__.py` - パッケージ初期化

## テンプレート (`templates/`)
- 裁判所・手続き種別別のテンプレートファイル

## その他
- `requirements.txt` - Python依存関係
- `credentials.json` - Google Sheets認証情報
- `.streamlit/` - Streamlit設定
- `backups/` - バックアップファイル（gitignore対象）

## 主要機能

### 1. データインポート機能
- JSONファイルからの一括インポート
- 手動でのデータ入力

### 2. データ管理機能
- Google Sheetsとの連携
- スプレッドシート一覧表示
- データの編集・削除

### 3. エクスポート機能
- 裁判所別テンプレートの使用
- Word/Excel形式での出力
- テンプレート変数の自動置換

### 4. システム管理
- レジストリ管理
- テンプレート管理
