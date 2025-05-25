import streamlit as st

st.title("手動データ登録")

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from utils.sheets_manager import SheetsManager
    from utils.styles import MAIN_CSS, get_success_html, get_green_button_html
    
    # CSS適用
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    
    @st.cache_resource
    def get_sheets_manager():
        return SheetsManager()
    
    sheets_manager = get_sheets_manager()
    
    if not sheets_manager.is_connected():
        st.error("Google Sheets接続エラー")
        st.stop()
    
    with st.form("add_creditor_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("基本情報")
            debtor_name = st.text_input("債務者名 *", placeholder="必須項目")
            company_name = st.text_input("会社名")
            branch_name = st.text_input("支店名")
            postal_code = st.text_input("郵便番号", placeholder="〒123-4567")
            address = st.text_area("住所", height=80)
            phone_number = st.text_input("電話番号", placeholder="03-1234-5678")
            fax_number = st.text_input("FAX番号", placeholder="03-1234-5679")
            claim_name = st.selectbox("債権名", ["", "貸付金", "立替金", "保証金", "その他"])
            claim_amount = st.text_input("債権額")
        
        with col2:
            st.subheader("日付・債権情報")
            contract_date = st.text_input("契約日", placeholder="2024年01月15日")
            first_borrowing_date = st.text_input("初回借入日", placeholder="2024年01月16日")
            last_borrowing_date = st.text_input("最終借入日", placeholder="2024年03月01日")
            last_payment_date = st.text_input("最終返済日", placeholder="2024年04月30日")
            original_creditor = st.text_input("原債権者")
            substitution_or_transfer = st.selectbox("代位弁済/債権譲渡", ["", "代位弁済", "債権譲渡"])
            transfer_date = st.text_input("債権移転日", placeholder="2024年05月01日")
            notes = st.text_area("備考", height=100)
        
        # スタイル統一された登録ボタン
        submitted = st.form_submit_button("スプレッドシートに登録", type="primary")
        
        if submitted:
            if not debtor_name.strip():
                st.error("債務者名は必須です")
            else:
                with st.spinner("データを登録中..."):
                    data = {
                        'debtor_name': debtor_name.strip(),
                        'company_name': company_name.strip(),
                        'branch_name': branch_name.strip(),
                        'postal_code': postal_code.strip(),
                        'address': address.strip(),
                        'phone_number': phone_number.strip(),
                        'fax_number': fax_number.strip(),
                        'claim_name': claim_name,
                        'claim_amount': claim_amount.strip(),
                        'contract_date': contract_date.strip(),
                        'first_borrowing_date': first_borrowing_date.strip(),
                        'last_borrowing_date': last_borrowing_date.strip(),
                        'last_payment_date': last_payment_date.strip(),
                        'original_creditor': original_creditor.strip(),
                        'substitution_or_transfer': substitution_or_transfer,
                        'transfer_date': transfer_date.strip(),
                        'notes': notes.strip()
                    }
                    
                    try:
                        spreadsheet = sheets_manager.get_or_create_spreadsheet(debtor_name.strip())
                        
                        if spreadsheet and sheets_manager.add_data(spreadsheet, data):
                            sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet.id}/edit?usp=sharing"
                            st.markdown(get_success_html("登録完了しました"), unsafe_allow_html=True)
                            
                            # スタイル統一されたボタンHTML使用
                            st.markdown("### スプレッドシートを確認")
                            st.markdown(
                                get_green_button_html(sheet_url, "スプレッドシートを開く"),
                                unsafe_allow_html=True
                            )
                            
                            # URLコピー用
                            st.text_input("スプレッドシートURL", value=sheet_url, help="Ctrl+C（またはCmd+C）でコピーできます")
                        else:
                            st.error("登録に失敗しました")
                            
                    except Exception as e:
                        st.error(f"登録失敗: {e}")
        
except Exception as e:
    st.error(f"エラー: {e}")
    import traceback
    st.text(traceback.format_exc())