import streamlit as st
import pandas as pd

st.title("スプレッドシート一覧")

try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    from utils.sheets_manager import SheetsManager
    from utils.styles import MAIN_CSS, get_green_button_html, get_info_html
    
    # CSS適用
    st.markdown(MAIN_CSS, unsafe_allow_html=True)
    
    @st.cache_resource
    def get_sheets_manager():
        return SheetsManager()
    
    sheets_manager = get_sheets_manager()
    
    if sheets_manager.is_connected():
        st.markdown('<span class="status-badge status-connected">Google Sheets 接続中</span>', unsafe_allow_html=True)
        
        sheets = sheets_manager.get_all_spreadsheets()
        
        if not sheets:
            st.markdown(get_info_html("スプレッドシートが作成されていません。データを登録すると自動で作成されます。"), unsafe_allow_html=True)
        else:
            # 債務者リストを作成
            debtor_names = sorted(list(set(sheet['debtor_name'] for sheet in sheets)))
            
            # 債務者選択
            selected_debtor = st.selectbox(
                "債務者を選択してください",
                options=["すべて表示"] + debtor_names,
                key="debtor_selector"
            )
            
            # 選択された債務者に応じてフィルタリング
            if selected_debtor == "すべて表示":
                filtered_sheets = sheets
            else:
                filtered_sheets = [sheet for sheet in sheets if sheet['debtor_name'] == selected_debtor]
            
            # スプレッドシート表示
            for i, sheet in enumerate(filtered_sheets):
                with st.container():
                    st.markdown(f"""
                    <div class="spreadsheet-card">
                        <h4 class="card-header">債務者: {sheet['debtor_name']}</h4>
                        <p class="card-subtitle">シート名: {sheet['sheet_name']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # ボタン行
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # データ表示状態をセッションで管理
                        view_key = f"viewing_{sheet['sheet_id']}"
                        data_key = f"data_{sheet['sheet_id']}"
                        
                        # データ確認/閉じるボタン（トグル機能）
                        is_viewing = st.session_state.get(view_key, False)
                        button_text = "データ表示を閉じる" if is_viewing else "データ確認"
                        
                        if st.button(button_text, key=f"toggle_view_{sheet['sheet_id']}", use_container_width=True):
                            if is_viewing:
                                # 現在表示中の場合は閉じる
                                st.session_state[view_key] = False
                                if data_key in st.session_state:
                                    del st.session_state[data_key]
                                st.rerun()
                            else:
                                # 現在非表示の場合は開く
                                with st.spinner("データを読み込み中..."):
                                    data = sheets_manager.get_data(sheet['sheet_id'])
                                    st.session_state[view_key] = True
                                    st.session_state[data_key] = data
                                    st.rerun()
                        
                        # データが表示状態の場合
                        if st.session_state.get(view_key, False) and data_key in st.session_state:
                            data = st.session_state[data_key]
                            
                            # データがリスト形式の場合はDataFrameに変換
                            if isinstance(data, list):
                                if len(data) > 1:
                                    headers = data[0]
                                    rows = data[1:]
                                    df = pd.DataFrame(rows, columns=headers)
                                else:
                                    df = pd.DataFrame()
                            else:
                                df = data
                            
                            if not df.empty:
                                # データ表示と行削除機能
                                st.subheader(f"{sheet['debtor_name']} のデータ一覧")
                                
                                # 列を選択して表示（sheet_row列は表示しない）
                                display_columns = [col for col in df.columns if col != 'sheet_row']
                                
                                # 削除ボタン付きテーブルを作成
                                for index, row in df.iterrows():
                                    sheet_row = row.get('sheet_row', index + 2)
                                    
                                    # 各行を一つのcontainerで表示
                                    with st.container():
                                        # 行データと削除ボタンを横並びに配置
                                        col_data, col_delete = st.columns([5, 1])
                                        
                                        with col_data:
                                            # 主要データを横に並べて表示
                                            main_info = []
                                            
                                            # 債権者名
                                            for name_col in ['債権者名', 'company_name', '会社名', '債権者']:
                                                if name_col in row and str(row[name_col]).strip():
                                                    main_info.append(f"**{row[name_col]}**")
                                                    break
                                            else:
                                                main_info.append("**不明**")
                                            
                                            # 債権額
                                            for amount_col in ['債権額', 'claim_amount', '金額']:
                                                if amount_col in row and str(row[amount_col]).strip():
                                                    main_info.append(f"金額: {row[amount_col]}円")
                                                    break
                                            else:
                                                main_info.append("金額: 0円")
                                            
                                            # ステータス
                                            status = row.get('ステータス', row.get('status', '未確認'))
                                            main_info.append(f"ステータス: {status}")
                                            
                                            # その他の主要項目（最大3つまで）
                                            other_cols = [col for col in display_columns[:5] 
                                                        if col not in ['債権者名', 'company_name', '会社名', '債権者', 
                                                                     '債権額', 'claim_amount', '金額', 'ステータス', 'status']]
                                            for col in other_cols[:3]:
                                                if col in row and str(row[col]).strip():
                                                    main_info.append(f"{col}: {row[col]}")
                                            
                                            # 行番号と主要情報を表示
                                            st.write(f"**行{sheet_row}:** " + " | ".join(main_info))
                                        
                                        with col_delete:
                                            delete_button_key = f"delete_row_{sheet['sheet_id']}_{sheet_row}_{index}"
                                            if st.button("削除", key=delete_button_key, type="secondary", use_container_width=True):
                                                try:
                                                    with st.spinner("削除中..."):
                                                        result = sheets_manager.delete_row(sheet['sheet_id'], sheet_row)
                                                        if result:
                                                            st.success(f"行{sheet_row}を削除しました")
                                                            # セッション状態のデータを更新
                                                            updated_data = sheets_manager.get_data(sheet['sheet_id'])
                                                            st.session_state[data_key] = updated_data
                                                            st.cache_resource.clear()
                                                            st.rerun()
                                                        else:
                                                            st.error("削除に失敗しました")
                                                except Exception as e:
                                                    st.error(f"削除エラー: {str(e)}")
                                        
                                        # 詳細情報は折りたたみで表示
                                        if len(display_columns) > 5:
                                            with st.expander(f"行{sheet_row}の詳細を表示"):
                                                detail_cols = st.columns(3)
                                                for i, col in enumerate(display_columns):
                                                    with detail_cols[i % 3]:
                                                        value = row.get(col, "")
                                                        if str(value).strip():
                                                            st.write(f"**{col}:** {value}")
                                        
                                        st.markdown("---")
                                    
                            else:
                                st.info("データがありません")
                    
                    with col2:
                        st.markdown(
                            get_green_button_html(sheet["url"], "新しいタブで開く"),
                            unsafe_allow_html=True
                        )
                    
                    with col3:
                        # 削除確認の状態管理
                        delete_confirm_key = f"delete_confirm_{sheet['sheet_id']}"
                        
                        if st.session_state.get(delete_confirm_key, False):
                            if st.button("本当に削除", key=f"confirm_delete_{sheet['sheet_id']}", use_container_width=True, type="secondary"):
                                if sheets_manager.delete_spreadsheet(sheet['sheet_id']):
                                    st.success(f"{sheet['debtor_name']}のスプレッドシートを削除しました")
                                    st.session_state[delete_confirm_key] = False
                                    st.rerun()
                                else:
                                    st.error("削除に失敗しました")
                            
                            if st.button("キャンセル", key=f"cancel_delete_{sheet['sheet_id']}", use_container_width=True):
                                st.session_state[delete_confirm_key] = False
                                st.rerun()
                        else:
                            if st.button("削除", key=f"delete_{sheet['sheet_id']}", use_container_width=True, type="secondary"):
                                st.session_state[delete_confirm_key] = True
                                st.rerun()
                    
                    # URL表示
                    st.text_input(
                        "スプレッドシートURL",
                        value=sheet['url'],
                        key=f"url_copy_{sheet['sheet_id']}",
                        help="Ctrl+C（またはCmd+C）でコピーできます"
                    )
                    
                    if i < len(filtered_sheets) - 1:
                        st.markdown("---")
                        
            # 選択された債務者のスプレッドシートがない場合
            if selected_debtor != "すべて表示" and not filtered_sheets:
                st.warning(f"{selected_debtor} のスプレッドシートが見つかりません")
                
    else:
        st.error("Google Sheets接続エラー")
        
except Exception as e:
    st.error(f"エラー: {e}")
    import traceback
    st.text(traceback.format_exc())