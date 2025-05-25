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
    
    st.markdown("ClaimExtract-GPTから出力されたJSONデータを貼り付けてください")
    
    # サンプルJSON表示
    with st.expander("JSONデータの例"):
        st.code(JSON_SAMPLE, language="json")
    
    # セッション状態の初期化
    if 'json_input_key' not in st.session_state:
        st.session_state.json_input_key = 0
    
    if 'registration_completed' not in st.session_state:
        st.session_state.registration_completed = False
    
    # 登録完了時の処理
    if st.session_state.registration_completed:
        st.markdown(get_success_html("データの登録が完了しました"), unsafe_allow_html=True)
        
        # セッション状態をリセット
        st.session_state.json_input_key += 1
        st.session_state.registration_completed = False
        st.rerun()
    
    # JSONデータ入力
    json_input = st.text_area(
        "JSONデータ",
        height=200,
        placeholder="JSONデータをここに貼り付けてください...",
        key=f"json_input_{st.session_state.json_input_key}"
    )
    
    # JSONデータの処理
    if json_input and json_input.strip():
        # パース処理
        with st.spinner("データを解析中..."):
            parsed_data, error = parse_json_data(json_input.strip())
        
        if error:
            st.error(f"エラー: {error}")
        else:
            st.markdown(get_success_html(f"{len(parsed_data)}件のデータを検出しました"), unsafe_allow_html=True)
            
            # 検証処理
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
                st.markdown(get_info_html(f"{len(valid_data)}件の有効なデータがあります"), unsafe_allow_html=True)
                
                if st.button("スプレッドシートに登録", type="primary", use_container_width=True):
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
                        st.session_state.registration_completed = True
                        st.rerun()
            else:
                st.error("有効なデータがありません。")
        
except Exception as e:
    st.error(f"エラー: {e}")
    import traceback
    st.text(traceback.format_exc())