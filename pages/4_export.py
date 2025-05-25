import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re
from openpyxl import load_workbook

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
    
    def replace_template_variables(text, creditor_data, debtor_name, court_name, case_number=""):
        """テンプレート変数を実際のデータで置換"""
        if not isinstance(text, str):
            return text
            
        result = text
        
        # 基本情報の置換
        result = result.replace("{debtor_name}", str(debtor_name))
        result = result.replace("{court_name}", str(court_name))
        result = result.replace("{case_number}", str(case_number))
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
        
        # 計算式の処理
        sum_patterns = re.findall(r'\{sum_claim_amount_(\d+)_to_(\d+)\}', result)
        for start, end in sum_patterns:
            start_idx, end_idx = int(start) - 1, int(end)
            sum_value = sum(float(str(creditor_data[i].get('債権額', 0)).replace(',', '')) if creditor_data[i].get('債権額') else 0
                           for i in range(start_idx, min(end_idx, len(creditor_data))))
            result = result.replace(f"{{sum_claim_amount_{start}_to_{end}}}", f"{int(sum_value):,}")
        
        return result
    
    def process_excel_template(template_path, creditor_data, debtor_name, court_name, case_number=""):
        """Excelテンプレートファイルを処理"""
        wb = load_workbook(template_path)
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            for row in ws.iter_rows():
                for cell in row:
                    if cell.value:
                        cell.value = replace_template_variables(
                            cell.value, creditor_data, debtor_name, court_name, case_number
                        )
        
        return wb
    
    # 裁判所選択
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
    
    # テンプレート使用タブ
    with tab1:
        st.subheader("債権者一覧表テンプレート使用")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_court = st.selectbox("裁判所を選択", courts)
            if selected_court == "その他":
                selected_court = st.text_input("裁判所名を入力")
        
        with col2:
            case_number = st.text_input("事件番号（任意）", placeholder="例：令和6年(フ)第123号")
        
        if template_manager.template_exists(selected_court):
            template_info = template_manager.get_template_info(selected_court)
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
                        
                        if data and len(data) > 1:
                            headers = data[0]
                            creditor_data = []
                            for row in data[1:]:
                                creditor_dict = {}
                                for i, header in enumerate(headers):
                                    creditor_dict[header] = row[i] if i < len(row) else ''
                                creditor_data.append(creditor_dict)
            
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
                                    
                                    if data and len(data) > 1:
                                        headers = data[0]
                                        creditor_data = []
                                        for row in data[1:]:
                                            creditor_dict = {}
                                            for i, header in enumerate(headers):
                                                creditor_dict[header] = row[i] if i < len(row) else ''
                                            creditor_data.append(creditor_dict)
                                        
                                        # セッション状態に保存
                                        st.session_state.creditor_data = creditor_data
                                        st.success("データを取得しました")
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
            
            # データが取得できた場合の処理
            if selected_debtor and creditor_data:
                # データプレビュー
                with st.expander("データプレビュー"):
                    df = pd.DataFrame(creditor_data)
                    st.dataframe(df, use_container_width=True)
                
                # エクスポート
                output_filename = st.text_input("出力ファイル名", 
                    value=f"{datetime.now().strftime('%Y%m%d')}_{selected_debtor}_債権者一覧表")
                
                if st.button("債権者一覧表作成・ダウンロード", type="primary", use_container_width=True):
                    with st.spinner("債権者一覧表を作成中..."):
                        try:
                            template_path = template_manager.get_template_path(selected_court)
                            
                            processed_wb = process_excel_template(
                                template_path, creditor_data, selected_debtor, selected_court, case_number
                            )
                            
                            output = io.BytesIO()
                            processed_wb.save(output)
                            output.seek(0)
                            
                            # 作成完了メッセージ
                            st.markdown(get_success_html("債権者一覧表を作成しました"), unsafe_allow_html=True)
                            
                            # Base64エンコード
                            import base64
                            b64 = base64.b64encode(output.getvalue()).decode()
                            
                            # 自動ダウンロードを試行するJavaScript
                            st.markdown(f"""
                            <script>
                            // 自動ダウンロードを実行
                            function downloadFile() {{
                                const link = document.createElement('a');
                                link.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}';
                                link.download = '{output_filename}.xlsx';
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                            }}
                            
                            // ページ読み込み後に実行
                            setTimeout(downloadFile, 100);
                            </script>
                            
                            <p style="color: #4CAF50; font-weight: bold;">
                            ダウンロードが自動で開始されます<br>
                            開始されない場合は下のボタンをクリックしてください
                            </p>
                            """, unsafe_allow_html=True)
                            
                            # フォールバック用ダウンロードボタン
                            st.download_button(
                                label="手動ダウンロード",
                                data=output.getvalue(),
                                file_name=f"{output_filename}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                            
                        except Exception as e:
                            st.error(f"処理エラー: {e}")
        else:
            st.warning(f"{selected_court}の債権者一覧表テンプレートが登録されていません")
    
    # テンプレート登録タブ
    with tab2:
        st.subheader("債権者一覧表テンプレート登録")
        
        # 裁判所選択（事件番号入力欄なし）
        selected_court_reg = st.selectbox("裁判所を選択", courts, key="court_registration")
        if selected_court_reg == "その他":
            selected_court_reg = st.text_input("裁判所名を入力", key="court_name_registration")
        
        st.write("債権者一覧表テンプレートを登録")
        
        new_desc = st.text_input("説明", value="債権者一覧表", placeholder="債権者一覧表の用途や特徴")
        new_file = st.file_uploader("Excelテンプレートファイル", type=['xlsx'])
        
        if st.button("テンプレート登録") and new_file:
            if template_manager.save_template(selected_court_reg, new_file.read(), new_desc):
                st.success(f"{selected_court_reg}の債権者一覧表テンプレートを登録しました")
                st.rerun()
        
        # テンプレート更新機能
        if template_manager.template_exists(selected_court_reg):
            st.markdown("---")
            st.write("既存テンプレートの更新")
            if st.checkbox("テンプレートを更新"):
                updated_file = st.file_uploader("新しいExcelファイル", type=['xlsx'], key="update")
                if updated_file and st.button("更新実行"):
                    if template_manager.save_template(selected_court_reg, updated_file.read()):
                        st.success("テンプレートを更新しました")
                        st.rerun()
        
        # テンプレート変数説明（このタブ内）
        st.markdown("---")
        with st.expander("テンプレート変数一覧"):
            for category, variables in TEMPLATE_VARIABLES.items():
                st.write(f"**{category}**")
                for var, desc in variables.items():
                    st.write(f"`{var}` → {desc}")
                st.write("")
            
            st.write("**記載例:**")
            st.code("""
債務者: {debtor_name}
裁判所: {court_name}
事件番号: {case_number}

債権者1: {company_name_1}
支店名: {branch_name_1}
住所: {postal_code_1} {address_1}
電話: {phone_number_1}
債権名: {claim_name_1}
債権額: {claim_amount_1}円
契約日: {contract_date_1}
原債権者: {original_creditor_1}

債権者2: {company_name_2}
住所: {postal_code_2} {address_2}
債権額: {claim_amount_2}円

合計金額: {sum_claim_amount_1_to_2}円
            """)
    
    # 使用方法
    st.markdown("---")
    st.subheader("使用方法")
    st.markdown("""
    **1. テンプレート準備**
    - 裁判所の債権者一覧表Excel書式を用意
    - セルに変数を記載（例: {company_name_1}）
    
    **2. テンプレート登録**
    - 「テンプレート登録」タブでExcelファイルをアップロード
    
    **3. 債権者一覧表作成**
    - 「テンプレート使用」タブで裁判所と債務者を選択
    - 「債権者一覧表作成・ダウンロード」で完成版をダウンロード
    """)
        
except Exception as e:
    st.error(f"エラー: {e}")
    import traceback
    st.text(traceback.format_exc())