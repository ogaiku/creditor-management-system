import streamlit as st
import sys
import os
import pandas as pd
import time

# パスの追加
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.sheets_manager import SheetsManager
from utils.styles import MAIN_CSS, get_green_button_html, get_info_html

# CSS適用
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# セッション状態の初期化
if 'viewing_sheets' not in st.session_state:
    st.session_state.viewing_sheets = {}
if 'sheet_data_cache' not in st.session_state:
    st.session_state.sheet_data_cache = {}
if 'delete_confirmations' not in st.session_state:
    st.session_state.delete_confirmations = {}

@st.cache_resource
def get_sheets_manager():
    return SheetsManager()

def clear_sheet_cache(sheet_id):
    """特定のシートのキャッシュをクリア"""
    if sheet_id in st.session_state.sheet_data_cache:
        del st.session_state.sheet_data_cache[sheet_id]
    if sheet_id in st.session_state.viewing_sheets:
        st.session_state.viewing_sheets[sheet_id] = False
    # 削除済み行の記録もクリア
    if f'deleted_rows_{sheet_id}' in st.session_state:
        del st.session_state[f'deleted_rows_{sheet_id}']

def get_sheet_data(sheets_manager, sheet_id):
    """シートデータを取得（キャッシュ機能付き）"""
    # キャッシュのタイムスタンプをチェック（5分で期限切れ）
    cache_key = f"cache_time_{sheet_id}"
    current_time = time.time()
    
    if cache_key in st.session_state:
        cache_time = st.session_state[cache_key]
        if current_time - cache_time > 300:  # 5分経過
            clear_sheet_cache(sheet_id)
    
    # キャッシュからデータを取得または新規取得
    if sheet_id not in st.session_state.sheet_data_cache:
        df = sheets_manager.get_data(sheet_id)
        if isinstance(df, list):
            df = pd.DataFrame(df)
        st.session_state.sheet_data_cache[sheet_id] = df
        st.session_state[cache_key] = current_time
    
    return st.session_state.sheet_data_cache[sheet_id]

def compact_sheet_data(sheets_manager, sheet_id):
    """シートの空白行を詰めて整理する"""
    try:
        # 現在のデータを取得
        df = get_sheet_data(sheets_manager, sheet_id)
        if df.empty:
            return True
        
        # 空白行以外のデータを取得
        non_empty_data = []
        for _, row in df.iterrows():
            # すべての列が空でない行のみを保持
            if any(str(val).strip() for val in row.values if pd.notna(val)):
                non_empty_data.append(row.to_dict())
        
        if not non_empty_data:
            return True
        
        # シートをクリアして再構築
        success = sheets_manager.clear_sheet_data(sheet_id)
        if not success:
            return False
        
        # ヘッダーを再追加
        headers = list(df.columns)
        if 'sheet_row' in headers:
            headers.remove('sheet_row')
        
        success = sheets_manager.add_headers(sheet_id, headers)
        if not success:
            return False
        
        # データを順次追加
        for data in non_empty_data:
            # sheet_row列を除外
            clean_data = {k: v for k, v in data.items() if k != 'sheet_row'}
            success = sheets_manager.append_data(sheet_id, clean_data)
            if not success:
                return False
            time.sleep(0.1)  # API制限対策
        
        # キャッシュをクリア
        clear_sheet_cache(sheet_id)
        
        return True
        
    except Exception as e:
        st.error(f"シート整理エラー: {str(e)}")
        return False

def display_sheet_data(sheet, sheets_manager):
    """シートデータの表示"""
    sheet_id = sheet['sheet_id']
    
    # データ表示トグル
    is_viewing = st.session_state.viewing_sheets.get(sheet_id, False)
    button_text = "データを閉じる" if is_viewing else "データ確認"
    
    if st.button(button_text, key=f"toggle_view_{sheet_id}", use_container_width=True):
        st.session_state.viewing_sheets[sheet_id] = not is_viewing
        if not st.session_state.viewing_sheets[sheet_id]:
            # 閉じる時はキャッシュをクリア
            clear_sheet_cache(sheet_id)
        st.rerun()
    
    # データ表示
    if st.session_state.viewing_sheets.get(sheet_id, False):
        with st.spinner("データを読み込み中..."):
            df = get_sheet_data(sheets_manager, sheet_id)
            
        if not df.empty:
            # 削除予定の行を追跡
            deleted_rows = st.session_state.get(f'deleted_rows_{sheet_id}', set())
            
            for index, row in df.iterrows():
                sheet_row = row.get('sheet_row', index + 2)
                
                # 既に削除済みの行はスキップ
                if sheet_row in deleted_rows:
                    continue
                
                # 空白行をスキップ
                if not any(str(val).strip() for val in row.values if pd.notna(val) and val != sheet_row):
                    continue
                
                # データ抽出
                creditor_name = extract_creditor_name(row)
                claim_amount = extract_claim_amount(row)
                status = row.get('ステータス', row.get('status', '未確認'))
                
                # 表示
                col_data, col_delete = st.columns([4, 1])
                
                with col_data:
                    st.write(f"**{creditor_name}** - {claim_amount}円 (ステータス: {status})")
                
                with col_delete:
                    if st.button("削除", key=f"delete_row_{sheet_id}_{sheet_row}", help="この行を削除"):
                        if delete_sheet_row(sheets_manager, sheet_id, sheet_row):
                            st.success("削除しました")
                            # 削除済みリストに追加
                            if f'deleted_rows_{sheet_id}' not in st.session_state:
                                st.session_state[f'deleted_rows_{sheet_id}'] = set()
                            st.session_state[f'deleted_rows_{sheet_id}'].add(sheet_row)
                            # キャッシュをクリア
                            clear_sheet_cache(sheet_id)
                            time.sleep(0.5)  # API制限対策
                            st.rerun()
                
                # 詳細表示
                with st.expander("詳細を表示"):
                    display_columns = [col for col in df.columns if col != 'sheet_row']
                    for col in display_columns[:10]:
                        if col in row and str(row[col]).strip():
                            st.write(f"**{col}:** {row[col]}")
                
                st.markdown("---")
        else:
            st.info("データがありません")

def extract_creditor_name(row):
    """債権者名を抽出"""
    name_columns = ['債権者名', 'company_name', '会社名', '債権者']
    for col in name_columns:
        if col in row and str(row[col]).strip():
            return row[col]
    return "不明"

def extract_claim_amount(row):
    """債権額を抽出"""
    amount_columns = ['債権額', 'claim_amount', '金額']
    for col in amount_columns:
        if col in row and str(row[col]).strip():
            return row[col]
    return "0"

def delete_sheet_row(sheets_manager, sheet_id, sheet_row):
    """行を削除"""
    try:
        result = sheets_manager.delete_row(sheet_id, sheet_row)
        return result
    except Exception as e:
        st.error(f"削除エラー: {str(e)}")
        return False

def main():
    st.title("スプレッドシート一覧")
    
    try:
        sheets_manager = get_sheets_manager()
        
        if not sheets_manager.is_connected():
            st.error("Google Sheets接続エラー")
            return
        
        st.markdown('<span class="status-badge status-connected">Google Sheets 接続中</span>', unsafe_allow_html=True)
        
        # スプレッドシート一覧を取得
        sheets = sheets_manager.get_all_spreadsheets()
        
        if not sheets:
            st.markdown(get_info_html("スプレッドシートが作成されていません。データを登録すると自動で作成されます。"), unsafe_allow_html=True)
            return
        
        # 重複チェック（URL重複の場合は最新のものだけを保持）
        unique_sheets = {}
        for sheet in sheets:
            key = (sheet['debtor_name'], sheet['url'])
            if key not in unique_sheets or sheet.get('created_at', '') > unique_sheets[key].get('created_at', ''):
                unique_sheets[key] = sheet
        
        sheets = list(unique_sheets.values())
        debtor_names = sorted(list(set(sheet['debtor_name'] for sheet in sheets)))
        
        # 債務者フィルター（複数債務者がいる場合のみ表示）
        if len(debtor_names) > 1:
            selected_debtor = st.selectbox(
                "債務者を選択してください",
                options=["すべて表示"] + debtor_names,
                key="debtor_selector"
            )
        else:
            selected_debtor = "すべて表示"
        
        # フィルタリング
        if selected_debtor == "すべて表示":
            filtered_sheets = sheets
        else:
            filtered_sheets = [sheet for sheet in sheets if sheet['debtor_name'] == selected_debtor]
        
        # 各シートの表示
        for i, sheet in enumerate(filtered_sheets):
            with st.container():
                # シート情報表示
                st.markdown(f"""
                <div class="spreadsheet-card">
                    <h4 class="card-header">債務者: {sheet['debtor_name']}</h4>
                    <p class="card-subtitle">シート名: {sheet['sheet_name']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(
                        get_green_button_html(sheet["url"], "新しいタブで開く"),
                        unsafe_allow_html=True
                    )
                
                with col2:
                    # スプレッドシート削除（確認付き）
                    delete_key = f"delete_sheet_{sheet['sheet_id']}"
                    
                    if st.session_state.delete_confirmations.get(delete_key, False):
                        # 確認モード
                        col_confirm, col_cancel = st.columns(2)
                        
                        with col_confirm:
                            if st.button("削除実行", key=f"confirm_{delete_key}", type="primary", use_container_width=True):
                                if sheets_manager.delete_spreadsheet(sheet['sheet_id']):
                                    st.success("削除しました")
                                    st.session_state.delete_confirmations[delete_key] = False
                                    clear_sheet_cache(sheet['sheet_id'])
                                    st.cache_resource.clear()
                                    time.sleep(0.5)  # API制限対策
                                    st.rerun()
                                else:
                                    st.error("削除に失敗しました")
                        
                        with col_cancel:
                            if st.button("取消", key=f"cancel_{delete_key}", type="secondary", use_container_width=True):
                                st.session_state.delete_confirmations[delete_key] = False
                                st.rerun()
                    else:
                        # 通常モード
                        if st.button("削除", key=delete_key, help="スプレッドシートを削除", use_container_width=True):
                            st.session_state.delete_confirmations[delete_key] = True
                            st.rerun()
                
                # データ確認ボタンを1行下に移動
                display_sheet_data(sheet, sheets_manager)
                
                # URL表示
                st.text_input(
                    "スプレッドシートURL",
                    value=sheet['url'],
                    key=f"url_copy_{sheet['sheet_id']}",
                    help="Ctrl+C（またはCmd+C）でコピーできます"
                )
                
                if i < len(filtered_sheets) - 1:
                    st.markdown("---")
        
        if selected_debtor != "すべて表示" and not filtered_sheets:
            st.warning(f"{selected_debtor} のスプレッドシートが見つかりません")
    
    except Exception as e:
        st.error(f"エラー: {e}")
        import traceback
        st.text(traceback.format_exc())

if __name__ == "__main__":
    main()