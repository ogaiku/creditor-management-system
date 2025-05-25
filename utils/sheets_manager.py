"""
Google Sheets操作管理
"""

import os
import streamlit as st
import pandas as pd
from datetime import datetime

class SheetsManager:
    def __init__(self):
        self.client = None
        self.gc = None  # エイリアス追加
        self.init_client()
    
    def init_client(self):
        """Google Sheetsクライアントを初期化"""
        try:
            # Streamlit Secretsから認証情報を取得を優先
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                self._init_from_secrets()
            elif os.path.exists('credentials.json'):
                self._init_from_file()
            else:
                st.warning("Google Sheets認証情報が設定されていません")
                self.client = None
                self.gc = None
            
        except Exception as e:
            st.error(f"Google Sheets接続エラー: {str(e)}")
            self.client = None
            self.gc = None
    
    def _init_from_file(self):
        """credentials.jsonからの初期化"""
        import gspread
        from google.oauth2.service_account import Credentials
        
        # Google Sheets API のスコープを直接定義
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_file(
            'credentials.json', scopes=scopes
        )
        self.client = gspread.authorize(credentials)
        self.gc = self.client  # エイリアス設定
    
    def _init_from_secrets(self):
        """Streamlit Secretsからの初期化"""
        import gspread
        from google.oauth2.service_account import Credentials
        
        try:
            # Google Sheets API のスコープを直接定義
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            # Streamlit Secretsから認証情報を取得
            credentials_info = dict(st.secrets['gcp_service_account'])
            
            credentials = Credentials.from_service_account_info(
                credentials_info, scopes=scopes
            )
            self.client = gspread.authorize(credentials)
            self.gc = self.client  # エイリアス設定
            
        except Exception as e:
            st.error(f"Google Sheets認証エラー: {str(e)}")
            self.client = None
            self.gc = None
            raise e
    
    def is_connected(self):
        """接続状態を確認"""
        return self.client is not None
    
    def get_data_by_id(self, spreadsheet_id, sheet_name=None):
        """
        スプレッドシートIDから直接データを取得
        
        Args:
            spreadsheet_id (str): スプレッドシートのID
            sheet_name (str, optional): シート名。指定しない場合は最初のシートを使用
        
        Returns:
            list: スプレッドシートのデータ（行の配列）
        """
        try:
            if not self.gc:
                st.error("Google Sheetsクライアントが接続されていません")
                return None
                
            # スプレッドシートを開く
            spreadsheet = self.gc.open_by_key(spreadsheet_id)
            
            # シート名が指定されていない場合は最初のシートを使用
            if sheet_name:
                worksheet = spreadsheet.worksheet(sheet_name)
            else:
                worksheet = spreadsheet.get_worksheet(0)  # 最初のシート
            
            # 全データを取得
            data = worksheet.get_all_values()
            
            # 空の行を除去
            filtered_data = []
            for row in data:
                if any(cell.strip() for cell in row):  # 空白でないセルがある行のみ
                    filtered_data.append(row)
            
            return filtered_data
            
        except Exception as e:
            st.error(f"スプレッドシート取得エラー: {e}")
            return None
    
    def list_spreadsheets(self):
        """スプレッドシート一覧を取得（エクスポート機能用）"""
        if not self.client:
            return []
            
        try:
            spreadsheets = self.client.list_spreadsheet_files()
            debt_sheets = []
            
            for sheet in spreadsheets:
                if "債権者データ_" in sheet['name']:
                    parts = sheet['name'].split('_')
                    if len(parts) >= 2:
                        debtor_name = parts[1]
                        debt_sheets.append({
                            'name': debtor_name,
                            'id': sheet['id'],
                            'sheet_id': sheet['id'],  # 両方のキーを追加
                            'url': f"https://docs.google.com/spreadsheets/d/{sheet['id']}/edit?usp=sharing"
                        })
            
            return debt_sheets
            
        except Exception as e:
            st.error(f"スプレッドシート一覧取得エラー: {e}")
            return []
    
    def get_data(self, sheet_info):
        """スプレッドシートからデータを取得（pandas DataFrame形式）"""
        if not self.client:
            return pd.DataFrame()
            
        try:
            # sheet_infoの形式チェック - 修正版
            if isinstance(sheet_info, dict):
                # 'id', 'sheet_id', またはその他のIDキーを探す
                sheet_id = sheet_info.get('id') or sheet_info.get('sheet_id')
                if not sheet_id:
                    st.error(f"sheet_info に 'id' または 'sheet_id' キーが見つかりません。利用可能なキー: {list(sheet_info.keys())}")
                    return pd.DataFrame()
            else:
                sheet_id = sheet_info
            
            if not sheet_id:
                st.error("スプレッドシートIDが無効です")
                return pd.DataFrame()
                
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 全ての値を取得
            all_values = worksheet.get_all_values()
            
            if not all_values:
                return pd.DataFrame()
            
            # ヘッダー行とデータ行を分離
            headers = all_values[0]
            data_rows = all_values[1:]
            
            # 空の行を除去してDataFrameを作成
            filtered_rows = []
            for i, row in enumerate(data_rows, start=2):  # 行番号は2から開始（ヘッダーが1行目）
                if any(cell.strip() for cell in row):
                    # 行番号を追加（Google Sheetsの実際の行番号）
                    row_with_number = row + [i] if len(row) < len(headers) + 1 else row
                    filtered_rows.append(row_with_number)
            
            if not filtered_rows:
                return pd.DataFrame()
            
            # DataFrame作成（sheet_row列を追加）
            df_headers = headers + ['sheet_row']
            df = pd.DataFrame(filtered_rows, columns=df_headers[:len(filtered_rows[0])])
            
            return df
            
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            return pd.DataFrame()
    
    def clear_sheet_data(self, sheet_id):
        """シートのデータ部分をクリア（ヘッダーは残す）"""
        if not self.client:
            return False
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 全ての値を取得して行数を確認
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:  # ヘッダーのみまたは空の場合
                return True
            
            # データ行をクリア（2行目以降）
            last_row = len(all_values)
            if last_row > 1:
                worksheet.batch_clear([f'A2:Z{last_row}'])
            
            return True
            
        except Exception as e:
            st.error(f"シートクリアエラー: {e}")
            return False
    
    def add_headers(self, sheet_id, headers):
        """ヘッダー行を追加"""
        if not self.client:
            return False
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # ヘッダー行を設定
            end_col = chr(ord('A') + len(headers) - 1)
            worksheet.update(f'A1:{end_col}1', [headers])
            
            # ヘッダー行のフォーマット
            worksheet.format(f'A1:{end_col}1', {
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                'textFormat': {'bold': True}
            })
            
            return True
            
        except Exception as e:
            st.error(f"ヘッダー追加エラー: {e}")
            return False
    
    def append_data(self, sheet_id, data):
        """データを最後の行に追加"""
        if not self.client:
            return False
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 現在のデータの最後の行を取得
            all_values = worksheet.get_all_values()
            next_row = len(all_values) + 1
            
            # データを行形式に変換
            if isinstance(data, dict):
                # ヘッダーの順序に従ってデータを配列に変換
                headers = all_values[0] if all_values else []
                row_data = []
                for header in headers:
                    if header == 'sheet_row':
                        continue  # sheet_row列はスキップ
                    row_data.append(data.get(header, ''))
            else:
                row_data = data
            
            # データを追加
            end_col = chr(ord('A') + len(row_data) - 1)
            worksheet.update(f'A{next_row}:{end_col}{next_row}', [row_data])
            
            return True
            
        except Exception as e:
            st.error(f"データ追加エラー: {e}")
            return False
    
    def find_next_empty_row(self, sheet_id):
        """次の空行を見つける"""
        if not self.client:
            return 2  # デフォルトは2行目（ヘッダーの次）
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 全ての値を取得
            all_values = worksheet.get_all_values()
            
            # 空でない行の次の行番号を返す
            non_empty_rows = 0
            for row in all_values:
                if any(cell.strip() for cell in row):
                    non_empty_rows += 1
                else:
                    break
            
            return non_empty_rows + 1
            
        except Exception as e:
            st.error(f"空行検索エラー: {e}")
            return 2
    
    def create_spreadsheet(self, debtor_name):
        """債務者専用のスプレッドシートを作成"""
        if not self.client:
            return None
            
        try:
            from config.settings import CREDITOR_FIELDS
            
            # 重複しないタイムスタンプを追加
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sheet_name = f"債権者データ_{debtor_name}_{timestamp}"
            
            # スプレッドシート作成
            spreadsheet = self.client.create(sheet_name)
            
            # ワークシート取得
            worksheet = spreadsheet.sheet1
            
            # ヘッダー行を設定（重複を避けるため一意のヘッダーに）
            unique_headers = []
            for i, field in enumerate(CREDITOR_FIELDS):
                if field in unique_headers:
                    unique_headers.append(f"{field}_{i}")
                else:
                    unique_headers.append(field)
            
            worksheet.update('A1:T1', [unique_headers])
            
            # ヘッダー行のフォーマット
            worksheet.format('A1:T1', {
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9},
                'textFormat': {'bold': True}
            })
            
            # スプレッドシートを完全に公開（誰でも編集可能）
            spreadsheet.share('', perm_type='anyone', role='writer', notify=False)
            
            # ドメイン制限なしで誰でもアクセス可能に設定
            try:
                spreadsheet.share('', perm_type='anyone', role='writer', notify=False, with_link=True)
            except:
                pass  # 既に設定済みの場合はエラーを無視
            
            return spreadsheet
            
        except Exception as e:
            st.error(f"スプレッドシート作成エラー: {e}")
            return None
    
    def get_or_create_spreadsheet(self, debtor_name):
        """債務者のスプレッドシートを取得または作成（重複防止強化）"""
        if not self.client:
            return None
            
        try:
            # 既存のスプレッドシートを検索（より厳密な検索）
            spreadsheets = self.client.list_spreadsheet_files()
            existing_sheets = []
            
            for sheet in spreadsheets:
                # 完全一致または部分一致で債務者名を含むシートを検索
                if (f"債権者データ_{debtor_name}_" in sheet['name'] or 
                    sheet['name'] == f"債権者データ_{debtor_name}"):
                    existing_sheets.append(sheet)
            
            # 既存のシートがある場合は最新のものを返す
            if existing_sheets:
                # 作成日時でソート（最新を取得）
                latest_sheet = max(existing_sheets, key=lambda x: x.get('createdTime', ''))
                existing_sheet = self.client.open_by_key(latest_sheet['id'])
                
                # 既存のスプレッドシートも公開設定を確認
                try:
                    existing_sheet.share('', perm_type='anyone', role='writer', notify=False)
                except:
                    pass
                    
                st.info(f"既存のスプレッドシートを使用します: {latest_sheet['name']}")
                return existing_sheet
            
            # 見つからない場合は新規作成
            st.info(f"{debtor_name} の新しいスプレッドシートを作成します")
            return self.create_spreadsheet(debtor_name)
            
        except Exception as e:
            st.error(f"スプレッドシート取得エラー: {e}")
            return None
    
    def add_data(self, spreadsheet, data):
        """スプレッドシートにデータを追加（重複チェック強化）"""
        if not spreadsheet:
            return False
            
        try:
            worksheet = spreadsheet.sheet1
            
            # 既存データをチェックして重複を防ぐ
            existing_data = worksheet.get_all_values()
            if len(existing_data) > 1:  # ヘッダー行以外にデータがある場合
                # 同じ債権者名と債権額の組み合わせがないかチェック
                company_name = data.get('company_name', '')
                claim_amount = data.get('claim_amount', '')
                
                for row in existing_data[1:]:  # ヘッダー行をスキップ
                    if len(row) >= 3 and row[2] == company_name and row[9] == str(claim_amount):
                        st.warning(f"同じデータが既に存在します: {company_name}")
                        return True  # 重複として処理成功扱い
            
            # 次の空行を見つける
            next_row = self.find_next_empty_row(spreadsheet.id)
            
            # IDは行番号-1（ヘッダー行を除く）
            data_id = next_row - 1
            
            row_data = [
                data_id,  # ID
                data.get('debtor_name', ''),
                data.get('company_name', ''),
                data.get('branch_name', ''),
                data.get('postal_code', ''),
                data.get('address', ''),
                data.get('phone_number', ''),
                data.get('fax_number', ''),
                data.get('claim_name', ''),
                data.get('claim_amount', ''),
                data.get('contract_date', ''),
                data.get('first_borrowing_date', ''),
                data.get('last_borrowing_date', ''),
                data.get('last_payment_date', ''),
                data.get('original_creditor', ''),
                data.get('substitution_or_transfer', ''),
                data.get('transfer_date', ''),
                '未確認',  # ステータス
                data.get('notes', ''),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            worksheet.update(f'A{next_row}:T{next_row}', [row_data])
            return True
            
        except Exception as e:
            st.error(f"データ追加エラー: {e}")
            return False
    
    def delete_spreadsheet(self, sheet_id):
        """スプレッドシートを削除"""
        if not self.client:
            return False
            
        try:
            # スプレッドシートを取得
            spreadsheet = self.client.open_by_key(sheet_id)
            
            # スプレッドシートを削除（ゴミ箱に移動）
            self.client.del_spreadsheet(sheet_id)
            
            return True
            
        except Exception as e:
            st.error(f"スプレッドシート削除エラー: {e}")
            return False
    
    def delete_row(self, sheet_id, row_number):
        """指定した行を削除"""
        if not self.client:
            return False
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 行を削除（row_numberは1ベース）
            worksheet.delete_rows(row_number)
            return True
            
        except Exception as e:
            st.error(f"行削除エラー: {str(e)}")
            return False
    
    def update_row(self, sheet_id, row_number, row_data):
        """指定した行のデータを更新"""
        if not self.client:
            return False
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 更新日時を最後に追加
            if len(row_data) >= 20:
                row_data[19] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 行を更新（A列からT列まで）
            worksheet.update(f'A{row_number}:T{row_number}', [row_data])
            return True
            
        except Exception as e:
            st.error(f"行更新エラー: {e}")
            return False
    
    def get_all_spreadsheets(self):
        """すべての債権者スプレッドシートを取得"""
        if not self.client:
            return []
            
        try:
            spreadsheets = self.client.list_spreadsheet_files()
            debt_sheets = []
            
            for sheet in spreadsheets:
                if "債権者データ_" in sheet['name']:
                    parts = sheet['name'].split('_')
                    if len(parts) >= 2:
                        debtor_name = parts[1]
                        debt_sheets.append({
                            'debtor_name': debtor_name,
                            'sheet_name': sheet['name'],
                            'sheet_id': sheet['id'],
                            'url': f"https://docs.google.com/spreadsheets/d/{sheet['id']}/edit?usp=sharing"
                        })
            
            return debt_sheets
            
        except Exception as e:
            st.error(f"スプレッドシート一覧取得エラー: {e}")
            return []
