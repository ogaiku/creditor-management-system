import streamlit as st

st.title("JSON一括取り込み")

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from utils.sheets_manager import SheetsManager
    from utils.data_processor import parse_json_data, validate_creditor_data
    from utils.styles import MAIN_CSS, get_success_html, get_info_html, get_warning_html
    from config.settings import JSON_SAMPLE
    
    # CSS適用
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    
    @st.cache_resource
    def get_sheets_manager():
        return SheetsManager()
    
    sheets_manager = get_sheets_manager()
    
    if not sheets_manager.is_connected():
        st.error("Google Sheets接続エラー")
        st.stop()
    
    st.markdown("ClaimExtract-GPTから出力されたJSONデータを貼り付けて、Ctrl+Enterまたは登録ボタンをクリックしてください")
    
    # サンプルJSON表示
    with st.expander("JSONデータの例"):
        st.code(JSON_SAMPLE, language="json")
    
    # セッション状態の初期化
    if 'json_input_key' not in st.session_state:
        st.session_state.json_input_key = 0
    
    if 'last_processed_json' not in st.session_state:
        st.session_state.last_processed_json = ""
    
    # JSONデータ入力
    json_input = st.text_area(
        "JSONデータ（入力後 Ctrl+Enter で自動登録）",
        height=200,
        placeholder="JSONデータをここに貼り付けて、Ctrl+Enterを押してください...",
        key=f"json_input_{st.session_state.json_input_key}",
        help="データを貼り付けた後、Ctrl+Enter（Mac: Cmd+Enter）を押すと自動的に解析・登録されます"
    )
    
    # 登録ボタン
    manual_submit = st.button("スプレッドシートに登録", type="primary", use_container_width=True)
    
    # JSONデータの自動処理判定
    should_process = False
    
    if json_input and json_input.strip():
        if json_input.strip() != st.session_state.last_processed_json or manual_submit:
            should_process = True
    
    # JSONデータの処理
    if should_process:
        st.session_state.last_processed_json = json_input.strip()
        
        # パース処理
        with st.spinner("データを解析・登録中..."):
            parsed_data, error = parse_json_data(json_input.strip())
        
        if error:
            st.error(f"JSON解析エラー: {error}")
        else:
            # 検証と登録処理
            valid_data = []
            error_count = 0
            
            for data in parsed_data:
                errors = validate_creditor_data(data)
                if errors:
                    error_count += 1
                    st.error(f"検証エラー ({data.get('debtor_name', '不明')}): {', '.join(errors)}")
                else:
                    valid_data.append(data)
            
            if error_count > 0:
                st.markdown(get_warning_html(f"{error_count}件のデータに検証エラーがあります"), unsafe_allow_html=True)
            
            if valid_data:
                # 即座に登録実行
                success_count = 0
                progress_bar = st.progress(0)
                
                for i, data in enumerate(valid_data):
                    progress_bar.progress((i + 1) / len(valid_data))
                    
                    try:
                        debtor_name = data.get('debtor_name', '').strip()
                        spreadsheet = sheets_manager.get_or_create_spreadsheet(debtor_name)
                        
                        if spreadsheet and sheets_manager.add_data(spreadsheet, data):
                            success_count += 1
                    except Exception as e:
                        st.error(f"処理エラー ({data.get('debtor_name', '不明')}): {e}")
                
                progress_bar.empty()
                
                if success_count > 0:
                    st.markdown(get_success_html(f"{success_count}件のデータを登録しました"), unsafe_allow_html=True)
                    
                    # 入力エリアをクリア
                    st.session_state.json_input_key += 1
                    st.session_state.last_processed_json = ""
                    
                    # 新しい入力の案内
                    st.info("新しいJSONデータを入力できます")
                    st.rerun()
            else:
                st.error("有効なデータがありません。")
    
    # 使用方法の説明
    st.markdown("---")
    st.markdown("### 使用方法")
    st.markdown("""
    1. JSONデータを上のテキストエリアに貼り付け
    2. Ctrl+Enter（Mac: Cmd+Enter）を押すか「スプレッドシートに登録」ボタンをクリック
    3. 登録完了後、すぐに次のデータを入力可能
    """)
        
except Exception as e:
    st.error(f"エラー: {e}")
    import traceback
    st.text(traceback.format_exc())