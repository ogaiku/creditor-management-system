import streamlit as st
import pandas as pd
from datetime import datetime
from utils.constants import COURTS, PROCEDURE_TYPES
from utils.styles import get_success_html

def render_template_usage_tab(data_handler, template_processor, sheets_manager, template_manager):
    """テンプレート使用タブをレンダリング"""
    st.subheader("債権者一覧表テンプレート使用")
    
    # 裁判所と手続種別の選択
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_court = st.selectbox("裁判所を選択", COURTS)
        if selected_court == "その他":
            selected_court = st.text_input("裁判所名を入力")
    
    with col2:
        procedure_type = st.selectbox("手続種別を選択", PROCEDURE_TYPES)
    
    with col3:
        case_number = st.text_input("事件番号（任意）", placeholder="例：令和6年(フ)第123号")
    
    template_key = template_processor.get_template_key(selected_court, procedure_type)
    
    if template_manager.template_exists(template_key):
        template_info = template_manager.get_template_info(template_key)
        if template_info:  # template_infoがNoneでないことを確認
            st.success(f"{selected_court} - {procedure_type} のテンプレートが利用可能です")
            st.text(f"説明: {template_info.get('description', 'なし')}")
            st.text(f"最終更新: {template_info.get('last_modified', 'なし')}")
        else:
            st.warning(f"{selected_court} - {procedure_type} のテンプレート情報を取得できませんでした")
        
        # データ取得セクション
        render_data_acquisition_section(data_handler)
        
        # エクスポート機能
        selected_debtor = st.session_state.get('selected_debtor')
        creditor_data = st.session_state.get('creditor_data')
        
        if selected_debtor and creditor_data:
            render_export_section(
                selected_debtor, creditor_data, selected_court, 
                procedure_type, case_number, template_processor, template_key
            )
    
    else:
        st.warning(f"{selected_court} - {procedure_type} のテンプレートが登録されていません")

def render_data_acquisition_section(data_handler):
    """データ取得セクションをレンダリング"""
    st.markdown("---")
    st.subheader("債務者データ取得")
    
    # データ取得方法の選択
    data_source = st.radio(
        "データ取得方法を選択してください",
        ["スプレッドシート一覧から選択", "スプレッドシートリンクを直接入力"],
        horizontal=True
    )
    
    if data_source == "スプレッドシート一覧から選択":
        selected_debtor, creditor_data = data_handler.get_data_from_spreadsheet_list()
        
        if selected_debtor and creditor_data:
            # セッション状態に保存
            st.session_state.selected_debtor = selected_debtor
            st.session_state.creditor_data = creditor_data
            
            st.success("データを取得しました")
            with st.expander("データプレビュー"):
                df = pd.DataFrame(creditor_data)
                st.dataframe(df, use_container_width=True)
    
    else:  # スプレッドシートリンクを直接入力
        selected_debtor, creditor_data = data_handler.get_data_from_url()

def render_export_section(selected_debtor, creditor_data, selected_court, procedure_type, case_number, template_processor, template_key):
    """エクスポートセクションをレンダリング"""
    st.markdown("---")
    st.subheader("エクスポート")
    
    output_filename = st.text_input("出力ファイル名", 
        value=f"{datetime.now().strftime('%Y%m%d')}_{selected_debtor}_{procedure_type}_債権者一覧表")
    
    if st.button("債権者一覧表をダウンロード", type="primary", use_container_width=True):
        with st.spinner("債権者一覧表を作成中..."):
            try:
                output, mime_type, file_ext, format_name = template_processor.process_template(
                    template_key, creditor_data, selected_debtor, selected_court, procedure_type, case_number
                )
                
                # 作成完了メッセージ
                st.markdown(
                    get_success_html(f"{procedure_type}の債権者一覧表が作成されました ({format_name}形式)"), 
                    unsafe_allow_html=True
                )
                
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