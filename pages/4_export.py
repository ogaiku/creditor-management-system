import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re
from openpyxl import load_workbook
from docx import Document

st.title("エクスポート機能")

# テンプレート管理タブ
tab1, tab2 = st.tabs(["テンプレート使用", "テンプレート登録"])

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from utils.sheets_manager import SheetsManager
    from utils.template_manager import TemplateManager
    from utils.styles import MAIN_CSS, get_success_html, get_warning_html
    
    # CSS適用
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    
    @st.cache_resource
    def get_managers():
        return SheetsManager(), TemplateManager()
    
    sheets_manager, template_manager = get_managers()
    
    if not sheets_manager.is_connected():
        st.error("Google Sheets接続エラー")
        st.stop()
    
    # テンプレート変数の定義
    TEMPLATE_VARIABLES = {
        "債務者情報": {
            "{debtor_name}": "債務者名",
            "{court_name}": "裁判所名",
            "{case_number}": "事件番号",
            "{procedure_type}": "手続種別（個人再生/自己破産）",
            "{today}": "今日の日付（YYYY年MM月DD日）",
            "{today_slash}": "今日の日付（YYYY/MM/DD）",
            "{total_creditors}": "債権者総数",
            "{total_claim_amount}": "債権金額総計"
        },
        "債権者情報（n=1,2,3...で番号指定）": {
            "{id_n}": "ID",
            "{company_name_n}": "会社名",
            "{branch_name_n}": "支店名", 
            "{postal_code_n}": "郵便番号",
            "{address_n}": "住所",
            "{phone_number_n}": "電話番号",
            "{fax_number_n}": "FAX番号",
            "{claim_name_n}": "債権名",
            "{claim_amount_n}": "債権額",
            "{contract_date_n}": "契約日",
            "{first_borrowing_date_n}": "初回借入日",
            "{last_borrowing_date_n}": "最終借入日", 
            "{last_payment_date_n}": "最終返済日",
            "{original_creditor_n}": "原債権者",
            "{substitution_or_transfer_n}": "代位弁済/債権譲渡",
            "{transfer_date_n}": "債権移転日",
            "{status_n}": "ステータス",
            "{notes_n}": "備考",
            "{registration_date_n}": "登録日"
        },
        "計算・集計": {
            "{sum_claim_amount_1_to_n}": "1番目からn番目までの債権額合計",
            "{creditor_rank_n}": "n番目の債権者順位（1,2,3...）"
        }
    }
    
    def handle_dataframe_conversion(data):
        """DataFrameをリスト形式に変換"""
        # None チェック
        if data is None:
            return None, None
            
        # DataFrameの場合
        if isinstance(data, pd.DataFrame):
            if data.empty:
                return None, None
            headers = data.columns.tolist()
            creditor_data = data.to_dict('records')
            return headers, creditor_data
            
        # リストの場合（従来の形式）
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

    def replace_template_variables(text, creditor_data, debtor_name, court_name, procedure_type, case_number=""):
        """テンプレート変数を実際のデータで置換"""
        if not isinstance(text, str):
            return text
            
        result = text
        
        # 基本情報の置換
        result = result.replace("{debtor_name}", str(debtor_name))
        result = result.replace("{court_name}", str(court_name))
        result = result.replace("{case_number}", str(case_number))
        result = result.replace("{procedure_type}", str(procedure_type))
        result = result.replace("{today}", datetime.now().strftime('%Y年%m月%d日'))
        result = result.replace("{today_slash}", datetime.now().strftime('%Y/%m/%d'))
        result = result.replace("{total_creditors}", str(len(creditor_data)))
        
        # 債権金額総計の計算
        total_amount = sum(float(str(row.get('債権額', 0)).replace(',', '')) if row.get('債権額') else 0 for row in creditor_data)
        result = result.replace("{total_claim_amount}", f"{int(total_amount):,}")
        
        # 債権者個別情報の置換
        for i, creditor in enumerate(creditor_data, 1):
            replacements = {
                f"{{id_{i}}}": str(creditor.get('ID', '')),
                f"{{company_name_{i}}}": str(creditor.get('会社名', '')),
                f"{{branch_name_{i}}}": str(creditor.get('支店名', '')),
                f"{{postal_code_{i}}}": str(creditor.get('郵便番号', '')),
                f"{{address_{i}}}": str(creditor.get('住所', '')),
                f"{{phone_number_{i}}}": str(creditor.get('電話番号', '')),
                f"{{fax_number_{i}}}": str(creditor.get('FAX番号', '')),
                f"{{claim_name_{i}}}": str(creditor.get('債権名', '')),
                f"{{claim_amount_{i}}}": str(creditor.get('債権額', '')),
                f"{{contract_date_{i}}}": str(creditor.get('契約日', '')),
                f"{{first_borrowing_date_{i}}}": str(creditor.get('初回借入日', '')),
                f"{{last_borrowing_date_{i}}}": str(creditor.get('最終借入日', '')),
                f"{{last_payment_date_{i}}}": str(creditor.get('最終返済日', '')),
                f"{{original_creditor_{i}}}": str(creditor.get('原債権者', '')),
                f"{{substitution_or_transfer_{i}}}": str(creditor.get('代位弁済/債権譲渡', '')),
                f"{{transfer_date_{i}}}": str(creditor.get('債権移転日', '')),
                f"{{status_{i}}}": str(creditor.get('ステータス', '')),
                f"{{notes_{i}}}": str(creditor.get('備考', '')),
                f"{{registration_date_{i}}}": str(creditor.get('登録日', '')),
                f"{{creditor_rank_{i}}}": str(i)
            }
            
            for var, value in replacements.items():
                result = result.replace(var, value)
        
        return result
        
    def process_excel_template(template_path, creditor_data, debtor_name, court_name, procedure_type, case_number=""):
        """Excelテンプレートファイルを処理"""
        wb = load_workbook(template_path)
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value:
                        cell.value = replace_template_variables(
                            cell.value, creditor_data, debtor_name, court_name, procedure_type, case_number
                        )
        
        return wb
    
    def process_word_template(template_path, creditor_data, debtor_name, court_name, procedure_type, case_number=""):
        """Wordテンプレートファイルを処理"""
        doc = Document(template_path)
        
        # 段落内のテキストを処理
        for paragraph in doc.paragraphs:
            if paragraph.text:
                new_text = replace_template_variables(
                    paragraph.text, creditor_data, debtor_name, court_name, procedure_type, case_number
                )
                if new_text != paragraph.text:
                    paragraph.clear()
                    paragraph.add_run(new_text)
        
        # テーブル内のテキストを処理
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        if paragraph.text:
                            new_text = replace_template_variables(
                                paragraph.text, creditor_data, debtor_name, court_name, procedure_type, case_number
                            )
                            if new_text != paragraph.text:
                                paragraph.clear()
                                paragraph.add_run(new_text)
        
        return doc
    
    def get_file_extension(file_path):
        """ファイル拡張子を取得"""
        import os
        return os.path.splitext(file_path)[1].lower()

    # 裁判所と手続種別の選択肢
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
    
    # テンプレート使用タブ
    with tab1:
        st.subheader("債権者一覧表テンプレート使用")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_court = st.selectbox("裁判所を選択", courts)
            if selected_court == "その他":
                selected_court = st.text_input("裁判所名を入力")
        
        with col2:
            procedure_type = st.selectbox("手続種別を選択", procedure_types)
        
        with col3:
            case_number = st.text_input("事件番号（任意）", placeholder="例：令和6年(フ)第123号")
        
        template_key = f"{selected_court}_{procedure_type}"
        
        if template_manager.template_exists(template_key):
            template_info = template_manager.get_template_info(template_key)
            st.success(f"{selected_court} - {procedure_type} のテンプレートが利用可能です")
            st.text(f"説明: {template_info['description']}")
            st.text(f"最終更新: {template_info['last_modified']}")
            
            # 債務者データ取得・エクスポート機能
            st.markdown("---")
            st.subheader("債務者データ取得")
            
            # データ取得方法の選択
            data_source = st.radio(
                "データ取得方法を選択してください",
                ["スプレッドシート一覧から選択", "スプレッドシートリンクを直接入力"],
                horizontal=True
            )
            
            selected_debtor = None
            creditor_data = None
            
            if data_source == "スプレッドシート一覧から選択":
                with st.spinner("債務者一覧を取得中..."):
                    spreadsheets = sheets_manager.list_spreadsheets()
                
                if not spreadsheets:
                    st.warning("債務者のスプレッドシートが見つかりません")
                else:
                    debtor_names = [sheet['name'] for sheet in spreadsheets]
                    selected_debtor = st.selectbox("債務者を選択", debtor_names)
                    
                    if selected_debtor:
                        with st.spinner(f"{selected_debtor}のデータを取得中..."):
                            selected_sheet = next(sheet for sheet in spreadsheets if sheet['name'] == selected_debtor)
                            data = sheets_manager.get_data(selected_sheet)
                        
                        # 修正: DataFrameの適切な判定
                        if data is not None:
                            if isinstance(data, pd.DataFrame) and not data.empty:
                                headers, creditor_data = handle_dataframe_conversion(data)
                                if creditor_data:
                                    st.success("データを取得しました")
                                    with st.expander("データプレビュー"):
                                        df = pd.DataFrame(creditor_data)
                                        st.dataframe(df, use_container_width=True)
                            elif isinstance(data, list) and len(data) > 1:
                                headers, creditor_data = handle_dataframe_conversion(data)
                                if creditor_data:
                                    st.success("データを取得しました")
                                    with st.expander("データプレビュー"):
                                        df = pd.DataFrame(creditor_data)
                                        st.dataframe(df, use_container_width=True)
                            else:
                                st.warning("データが見つかりませんでした")
                        else:
                            st.warning("データが見つかりませんでした")
            
            else:  # スプレッドシートリンクを直接入力
                st.write("**スプレッドシートリンクから直接データを取得**")
                
                # スプレッドシートリンク入力
                spreadsheet_url = st.text_input(
                    "スプレッドシートのリンクを貼り付けてください",
                    placeholder="https://docs.google.com/spreadsheets/d/...",
                    help="Google SheetsのURLを貼り付けてください"
                )
                
                # 債務者名入力（オプション）
                manual_debtor_name = st.text_input(
                    "債務者名（オプション - 空白の場合はスプレッドシートから自動取得）", 
                    placeholder="例：株式会社サンプル",
                    help="入力しない場合は、スプレッドシートのタイトルから自動で抽出します"
                )
                
                if spreadsheet_url:
                    if st.button("データを取得", type="secondary"):
                        with st.spinner("スプレッドシートからデータを取得中..."):
                            try:
                                # URLからスプレッドシートIDを抽出
                                match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', spreadsheet_url)
                                if not match:
                                    st.error("有効なGoogle SheetsのURLではありません")
                                else:
                                    spreadsheet_id = match.group(1)
                                    
                                    # スプレッドシート情報を取得
                                    spreadsheet = sheets_manager.gc.open_by_key(spreadsheet_id)
                                    
                                    # 債務者名を決定
                                    if manual_debtor_name.strip():
                                        selected_debtor = manual_debtor_name.strip()
                                    else:
                                        # スプレッドシートタイトルから債務者名を抽出
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
                                    st.info(f"債務者名: {selected_debtor}")
                                    
                                    # スプレッドシートデータを取得
                                    data = sheets_manager.get_data_by_id(spreadsheet_id)
                                    
                                    # 修正: DataFrameの適切な判定
                                    if data is not None:
                                        if isinstance(data, pd.DataFrame) and not data.empty:
                                            headers, creditor_data = handle_dataframe_conversion(data)
                                            if creditor_data:
                                                # セッション状態に保存
                                                st.session_state.creditor_data = creditor_data
                                                st.success("データを取得しました")
                                            else:
                                                st.error("スプレッドシートにデータが見つかりません")
                                        elif isinstance(data, list) and len(data) > 1:
                                            headers, creditor_data = handle_dataframe_conversion(data)
                                            if creditor_data:
                                                # セッション状態に保存
                                                st.session_state.creditor_data = creditor_data
                                                st.success("データを取得しました")
                                            else:
                                                st.error("スプレッドシートにデータが見つかりません")
                                        else:
                                            st.error("スプレッドシートにデータが見つかりません")
                                    else:
                                        st.error("スプレッドシートにデータが見つかりません")
                            
                            except Exception as e:
                                st.error(f"データ取得エラー: {e}")
                                st.write("スプレッドシートが共有されているか、URLが正しいか確認してください")
                
                # セッション状態から値を復元
                if 'selected_debtor' in st.session_state:
                    selected_debtor = st.session_state.selected_debtor
                if 'creditor_data' in st.session_state:
                    creditor_data = st.session_state.creditor_data
            
            # データが取得できた場合のダウンロード機能
            if selected_debtor and creditor_data:
                st.markdown("---")
                st.subheader("エクスポート")
                
                output_filename = st.text_input("出力ファイル名", 
                    value=f"{datetime.now().strftime('%Y%m%d')}_{selected_debtor}_{procedure_type}_債権者一覧表")
                
                if st.button("債権者一覧表をダウンロード", type="primary", use_container_width=True):
                    with st.spinner("債権者一覧表を作成中..."):
                        try:
                            template_path = template_manager.get_template_path(template_key)
                            file_extension = get_file_extension(template_path)
                            
                            # ファイル形式に応じた処理
                            if file_extension == ".docx":
                                # Word文書の処理
                                processed_doc = process_word_template(
                                    template_path, creditor_data, selected_debtor, selected_court, procedure_type, case_number
                                )
                                
                                output = io.BytesIO()
                                processed_doc.save(output)
                                output.seek(0)
                                
                                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                file_ext = "docx"
                                
                            else:
                                # Excel文書の処理
                                processed_wb = process_excel_template(
                                    template_path, creditor_data, selected_debtor, selected_court, procedure_type, case_number
                                )
                                
                                output = io.BytesIO()
                                processed_wb.save(output)
                                output.seek(0)
                                
                                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                file_ext = "xlsx"
                            
                            # 作成完了メッセージ
                            format_name = "Word" if file_extension == ".docx" else "Excel"
                            st.markdown(get_success_html(f"{procedure_type}の債権者一覧表が作成されました ({format_name}形式)"), unsafe_allow_html=True)
                            
                            # ダウンロードボタン
                            st.download_button(
                                label=f"ダウンロード ({format_name}形式)",
                                data=output.getvalue(),
                                file_name=f"{output_filename}.{file_ext}",
                                mime=mime_type,
                                use_container_width=True,
                                type="secondary"
                            )
                            
                            # ファイル情報
                            file_size = len(output.getvalue())
                            st.caption(f"ファイルサイズ: {file_size:,} バイト ({file_size/1024/1024:.2f} MB)")
                            
                        except Exception as e:
                            st.error(f"処理エラー: {e}")
                            st.write("エラー詳細:")
                            import traceback
                            st.text(traceback.format_exc())
        
        else:
            st.warning(f"{selected_court} - {procedure_type} のテンプレートが登録されていません")
    
    # テンプレート登録タブ
    with tab2:
        st.subheader("債権者一覧表テンプレート登録")
        st.info("テンプレート登録機能は準備中です")

except Exception as e:
    st.error(f"エクスポート機能の初期化エラー: {e}")
    st.write("詳細なエラー情報:")
    import traceback
    st.text(traceback.format_exc())
    
    st.markdown("---")
    st.subheader("トラブルシューティング")
    st.write("1. Google Sheetsの認証情報が正しく設定されているか確認")
    st.write("2. utils/ディレクトリのファイルが正常に読み込めるか確認")
    st.write("3. 必要なライブラリがインストールされているか確認")