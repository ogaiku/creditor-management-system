import streamlit as st
import pandas as pd
import re

class DataHandler:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
    
    def handle_dataframe_conversion(self, data):
        """DataFrameまたはリストをリスト形式に変換"""
        if data is None:
            return None, None
            
        # DataFrameの場合
        if isinstance(data, pd.DataFrame):
            if data.empty:
                return None, None
            headers = data.columns.tolist()
            creditor_data = data.to_dict('records')
            return headers, creditor_data
            
        # リストの場合
        elif isinstance(data, list) and len(data) > 1:
            headers = data[0]
            creditor_data = []
            for row in data[1:]:
                creditor_dict = {}
                for i, header in enumerate(headers):
                    creditor_dict[header] = row[i] if i < len(row) else ''
                creditor_data.append(creditor_dict)
            return headers, creditor_data
            
        return None, None

    def safe_get_spreadsheet_data_by_id(self, spreadsheet_id):
        """スプレッドシートIDから安全にデータを取得"""
        try:
            data = self.sheets_manager.get_data_by_id(spreadsheet_id)
            
            if data is None or not data or len(data) <= 1:
                return None
            
            return data
            
        except Exception as e:
            st.error(f"データ取得中にエラーが発生しました: {e}")
            return None

    def safe_get_data_from_sheet_info(self, sheet_info):
        """sheet_infoからデータを安全に取得"""
        try:
            # sheet_idキーがない場合は手動で追加
            if isinstance(sheet_info, dict):
                if 'sheet_id' not in sheet_info and 'id' in sheet_info:
                    sheet_info = sheet_info.copy()
                    sheet_info['sheet_id'] = sheet_info['id']
            
            data = self.sheets_manager.get_data(sheet_info)
            return data
            
        except Exception as e:
            st.error(f"データ取得中にエラーが発生しました: {e}")
            return None
    
    def get_data_from_spreadsheet_list(self):
        """スプレッドシート一覧からデータを取得"""
        with st.spinner("債務者一覧を取得中..."):
            spreadsheets = self.sheets_manager.list_spreadsheets()
        
        if not spreadsheets:
            st.warning("債務者のスプレッドシートが見つかりません")
            return None, None
        
        debtor_names = [sheet['name'] for sheet in spreadsheets]
        selected_debtor = st.selectbox("債務者を選択", debtor_names)
        
        if selected_debtor:
            with st.spinner(f"{selected_debtor}のデータを取得中..."):
                selected_sheet = next(sheet for sheet in spreadsheets if sheet['name'] == selected_debtor)
                data = self.safe_get_data_from_sheet_info(selected_sheet)
            
            if data is not None:
                if isinstance(data, pd.DataFrame) and not data.empty:
                    headers, creditor_data = self.handle_dataframe_conversion(data)
                    if creditor_data:
                        return selected_debtor, creditor_data
                elif isinstance(data, list) and len(data) > 1:
                    headers, creditor_data = self.handle_dataframe_conversion(data)
                    if creditor_data:
                        return selected_debtor, creditor_data
                
                st.warning("データが見つかりませんでした")
        
        return None, None
    
    def get_data_from_url(self):
        """URLから直接データを取得"""
        st.write("**スプレッドシートリンクから直接データを取得**")
        
        spreadsheet_url = st.text_input(
            "スプレッドシートのリンクを貼り付けてください",
            placeholder="https://docs.google.com/spreadsheets/d/...",
            help="Google SheetsのURLを貼り付けてください"
        )
        
        manual_debtor_name = st.text_input(
            "債務者名（オプション - 空白の場合はスプレッドシートから自動取得）", 
            placeholder="例：株式会社サンプル",
            help="入力しない場合は、スプレッドシートのタイトルから自動で抽出します"
        )
        
        if spreadsheet_url and st.button("データを取得", type="secondary"):
            return self._process_url_data(spreadsheet_url, manual_debtor_name)
        
        # セッション状態から値を復元
        selected_debtor = st.session_state.get('selected_debtor')
        creditor_data = st.session_state.get('creditor_data')
        
        return selected_debtor, creditor_data
    
    def _process_url_data(self, spreadsheet_url, manual_debtor_name):
        """URL入力からのデータ処理"""
        with st.spinner("スプレッドシートからデータを取得中..."):
            try:
                # URLからスプレッドシートIDを抽出
                match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
                if not match:
                    st.error("有効なGoogle SheetsのURLではありません")
                    return None, None
                
                spreadsheet_id = match.group(1)
                
                # スプレッドシート情報を取得
                try:
                    spreadsheet = self.sheets_manager.gc.open_by_key(spreadsheet_id)
                    
                    # 債務者名を決定
                    if manual_debtor_name.strip():
                        selected_debtor = manual_debtor_name.strip()
                    else:
                        sheet_title = spreadsheet.title
                        if "債権者データ_" in sheet_title:
                            parts = sheet_title.split('_')
                            if len(parts) >= 2:
                                selected_debtor = parts[1]
                            else:
                                selected_debtor = "不明な債務者"
                        else:
                            selected_debtor = sheet_title
                    
                    # セッション状態に保存
                    st.session_state.selected_debtor = selected_debtor
                    
                    # データ取得
                    data = self.safe_get_spreadsheet_data_by_id(spreadsheet_id)
                    
                    if data is not None and len(data) > 1:
                        headers, creditor_data = self.handle_dataframe_conversion(data)
                        if creditor_data:
                            st.session_state.creditor_data = creditor_data
                            st.success("データを取得しました")
                            
                            with st.expander("データプレビュー"):
                                df = pd.DataFrame(creditor_data)
                                st.dataframe(df, use_container_width=True)
                            
                            return selected_debtor, creditor_data
                        else:
                            st.error("データの変換に失敗しました")
                    else:
                        st.error("スプレッドシートにデータが見つかりません")
                
                except Exception as sheet_error:
                    st.error(f"スプレッドシートアクセスエラー: {sheet_error}")
                    st.write("スプレッドシートが共有されているか、URLが正しいか確認してください")
            
            except Exception as e:
                st.error(f"データ取得エラー: {e}")
        
        return None, None