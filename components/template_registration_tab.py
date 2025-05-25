import streamlit as st
import pandas as pd
import os
from utils.constants import COURTS, PROCEDURE_TYPES, TEMPLATE_VARIABLES
from utils.template_processor import TemplateProcessor

def render_template_registration_tab(template_manager):
    """テンプレート登録タブをレンダリング"""
    st.subheader("債権者一覧表テンプレート登録")
    
    # テンプレート登録フォーム
    render_registration_form(template_manager)
    
    # 既存テンプレート一覧
    render_existing_templates_list(template_manager)
    
    # テンプレート更新機能
    render_template_update_section(template_manager)
    
    # テンプレート変数説明
    render_template_variables_help()

def render_registration_form(template_manager):
    """テンプレート登録フォームをレンダリング"""
    col1, col2 = st.columns(2)
    
    with col1:
        # 裁判所選択
        selected_court_reg = st.selectbox("裁判所を選択", COURTS, key="court_registration")
        if selected_court_reg == "その他":
            selected_court_reg = st.text_input("裁判所名を入力", key="court_name_registration")
    
    with col2:
        # 手続種別選択
        procedure_type_reg = st.selectbox("手続種別を選択", PROCEDURE_TYPES, key="procedure_registration")
    
    template_key_reg = TemplateProcessor.get_template_key(selected_court_reg, procedure_type_reg)
    
    st.write(f"**{selected_court_reg} - {procedure_type_reg}** の債権者一覧表テンプレートを登録")
    
    new_desc = st.text_input("説明", value=f"{procedure_type_reg}用債権者一覧表", placeholder="テンプレートの用途や特徴")
    new_file = st.file_uploader("テンプレートファイル", type=['xlsx', 'docx'], help="ExcelファイルまたはWordファイルを選択してください")
    
    if st.button("テンプレート登録") and new_file:
        # ファイル拡張子をチェック
        file_extension = os.path.splitext(new_file.name)[1].lower()
        if file_extension in ['.xlsx', '.docx']:
            if template_manager.save_template(template_key_reg, new_file.read(), new_desc, file_extension):
                format_name = "Excel" if file_extension == ".xlsx" else "Word"
                st.success(f"{selected_court_reg} - {procedure_type_reg} の債権者一覧表テンプレートを登録しました ({format_name}形式)")
                st.rerun()
        else:
            st.error("Excelファイル(.xlsx)またはWordファイル(.docx)のみ対応しています")

def render_existing_templates_list(template_manager):
    """既存テンプレート一覧をレンダリング"""
    st.markdown("---")
    st.subheader("登録済みテンプレート一覧")
    
    registered_templates = []
    for court in COURTS[:-1]:  # "その他"を除く
        for proc_type in PROCEDURE_TYPES:
            key = TemplateProcessor.get_template_key(court, proc_type)
            if template_manager.template_exists(key):
                template_info = template_manager.get_template_info(key)
                template_path = template_manager.get_template_path(key)
                file_ext = TemplateProcessor.get_file_extension(template_path)
                format_name = "Excel" if file_ext == ".xlsx" else "Word" if file_ext == ".docx" else "不明"
                
                registered_templates.append({
                    "裁判所": court,
                    "手続種別": proc_type,
                    "形式": format_name,
                    "説明": template_info['description'],
                    "最終更新": template_info['last_modified']
                })
    
    if registered_templates:
        df_templates = pd.DataFrame(registered_templates)
        st.dataframe(df_templates, use_container_width=True)
    else:
        st.info("登録済みテンプレートはありません")

def render_template_update_section(template_manager):
    """テンプレート更新セクションをレンダリング"""
    col1, col2 = st.columns(2)
    
    with col1:
        selected_court_reg = st.selectbox("裁判所を選択", COURTS, key="court_update")
        if selected_court_reg == "その他":
            selected_court_reg = st.text_input("裁判所名を入力", key="court_name_update")
    
    with col2:
        procedure_type_reg = st.selectbox("手続種別を選択", PROCEDURE_TYPES, key="procedure_update")
    
    template_key_reg = TemplateProcessor.get_template_key(selected_court_reg, procedure_type_reg)
    
    # テンプレート更新機能
    if template_manager.template_exists(template_key_reg):
        st.markdown("---")
        st.write(f"**{selected_court_reg} - {procedure_type_reg}** の既存テンプレートを更新")
        if st.checkbox("テンプレートを更新"):
            updated_file = st.file_uploader("新しいファイル", type=['xlsx', 'docx'], key="update")
            updated_desc = st.text_input("更新説明", value=f"{procedure_type_reg}用債権者一覧表", key="update_desc")
            if updated_file and st.button("更新実行"):
                file_extension = os.path.splitext(updated_file.name)[1].lower()
                if file_extension in ['.xlsx', '.docx']:
                    if template_manager.save_template(template_key_reg, updated_file.read(), updated_desc, file_extension):
                        st.success("テンプレートを更新しました")
                        st.rerun()
                else:
                    st.error("Excelファイル(.xlsx)またはWordファイル(.docx)のみ対応しています")

def render_template_variables_help():
    """テンプレート変数説明をレンダリング"""
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
手続種別: {procedure_type}
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