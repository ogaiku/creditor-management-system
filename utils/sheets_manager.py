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
        self.init_client()
    
    def init_client(self):
        """Google Sheetsクライアントを初期化"""
        try:
            # credentials.jsonファイルを優先
            if os.path.exists('credentials.json'):
                self._init_from_file()
            elif 'GOOGLE_SHEETS_CREDENTIALS' in st.secrets:
                self._init_from_secrets()
            else:
                st.warning("Google Sheets認証情報が設定されていません")
                self.client = None
            
        except Exception as e:
            st.error(f"Google Sheets接続エラー: {str(e)}")
            self.client = None
    
    def _init_from_file(self):
        """credentials.jsonからの初期化"""
        import gspread
        from google.oauth2.service_account import Credentials
        from config.settings import GOOGLE_SHEETS_SCOPES
        
        credentials = Credentials.from_service_account_file(
            'credentials.json', scopes=GOOGLE_SHEETS_SCOPES
        )
        self.client = gspread.authorize(credentials)
    
    def _init_from_secrets(self):
        """Streamlit Secretsからの初期化"""
        import gspread
        from google.oauth2.service_account import Credentials
        from config.settings import GOOGLE_SHEETS_SCOPES
        
        credentials_info = st.secrets['GOOGLE_SHEETS_CREDENTIALS']
        credentials = Credentials.from_service_account_info(
            credentials_info, scopes=GOOGLE_SHEETS_SCOPES
        )
        self.client = gspread.authorize(credentials)
    
    def is_connected(self):
        """接続状態を確認"""
        return self.client is not None
    
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
        """債務者のスプレッドシートを取得または作成"""
        if not self.client:
            return None
            
        try:
            # 既存のスプレッドシートを検索
            spreadsheets = self.client.list_spreadsheet_files()
            for sheet in spreadsheets:
                if f"債権者データ_{debtor_name}" in sheet['name']:
                    # 既存のスプレッドシートも公開設定を確認
                    existing_sheet = self.client.open_by_key(sheet['id'])
                    try:
                        existing_sheet.share('', perm_type='anyone', role='writer', notify=False)
                    except:
                        pass
                    return existing_sheet
            
            # 見つからない場合は新規作成
            return self.create_spreadsheet(debtor_name)
            
        except Exception as e:
            st.error(f"スプレッドシート取得エラー: {e}")
            return None
    
    def add_data(self, spreadsheet, data):
        """スプレッドシートにデータを追加"""
        if not spreadsheet:
            return False
            
        try:
            worksheet = spreadsheet.sheet1
            
            # 空行を探す（ヘッダー行以降で最初の空行）
            all_values = worksheet.get_all_values()
            next_row = len([row for row in all_values if any(cell.strip() for cell in row)]) + 1
            
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
            st.error("Google Sheetsクライアントが接続されていません")
            return False
            
        try:
            st.info(f"削除開始: シートID={sheet_id[:10]}..., 行番号={row_number}")
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 行を削除（row_numberは1ベース）
            worksheet.delete_rows(row_number)
            st.success(f"Google Sheetsから行 {row_number} を削除しました")
            return True
            
        except Exception as e:
            st.error(f"行削除エラー: {str(e)}")
            import traceback
            st.text(traceback.format_exc())
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
    
    def get_data(self, sheet_id):
        """スプレッドシートからデータを取得"""
        if not self.client:
            return pd.DataFrame()
            
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.sheet1
            
            # 全ての値を取得
            all_values = worksheet.get_all_values()
            
            if len(all_values) < 2:  # ヘッダー行のみまたは空
                return pd.DataFrame()
            
            # ヘッダー行とデータ行を分離
            headers = all_values[0]
            data_rows = all_values[1:]
            
            # 空の行を除外しつつ、元の行番号を保持
            filtered_rows = []
            original_row_numbers = []
            
            for i, row in enumerate(data_rows):
                if any(cell.strip() for cell in row):
                    filtered_rows.append(row)
                    original_row_numbers.append(i + 2)  # ヘッダーが1行目なので+2
            
            if not filtered_rows:
                return pd.DataFrame()
            
            # DataFrameを作成
            df = pd.DataFrame(filtered_rows, columns=headers)
            
            # 空の列を除外
            df = df.loc[:, df.columns != '']
            
            # 実際のシート行番号を追加
            df['sheet_row'] = original_row_numbers
            
            return df
            
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            return pd.DataFrame()