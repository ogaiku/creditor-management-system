import streamlit as st
import os

def render_registry_info_tab(registry_utils):
    """レジストリ情報タブをレンダリング"""
    st.subheader("現在のレジストリ情報")
    
    # 統計情報を取得
    total_courts, total_templates, court_details = registry_utils.get_registry_statistics()
    
    if total_courts is None:
        st.info("レジストリが空です")
        return
    
    # メトリクス表示
    render_metrics(total_courts, total_templates, court_details)
    
    # 詳細表示
    render_court_details(court_details, registry_utils.template_manager)

def render_metrics(total_courts, total_templates, court_details):
    """メトリクス情報をレンダリング"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("登録裁判所数", total_courts)
    with col2:
        st.metric("総テンプレート数", total_templates)
    with col3:
        available_count = sum(1 for court in court_details if court["count"] > 0)
        st.metric("テンプレート保有裁判所", available_count)

def render_court_details(court_details, template_manager):
    """裁判所別詳細情報をレンダリング"""
    st.markdown("---")
    st.subheader("裁判所別テンプレート詳細")
    
    if not court_details:
        st.info("登録されているテンプレートはありません")
        return
    
    # テンプレートがある裁判所のみ表示
    courts_with_templates = [court for court in court_details if court["count"] > 0]
    
    if not courts_with_templates:
        st.info("テンプレートが登録されている裁判所はありません")
        return
    
    for court in courts_with_templates:
        with st.expander(f"{court['name']} - {court['count']}件"):
            render_court_templates(court, template_manager)

def render_court_templates(court, template_manager):
    """個別裁判所のテンプレート情報をレンダリング"""
    for procedure in court['procedures']:
        template_key = f"{court['name']}_{procedure}"
        template_info = template_manager.get_template_info(template_key)
        
        if template_info:
            st.markdown(f"**{procedure}**")
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.text(f"説明: {template_info.get('description', 'なし')}")
                st.text(f"作成日: {template_info.get('created_date', 'なし')}")
            
            with info_col2:
                st.text(f"最終更新: {template_info.get('last_modified', 'なし')}")
                file_path = template_info.get('file_path', '')
                exists = os.path.exists(file_path) if file_path else False
                st.text(f"ファイル: {'存在' if exists else '不存在'}")
            
            st.markdown("---")