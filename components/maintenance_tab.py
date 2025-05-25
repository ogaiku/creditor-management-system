import streamlit as st

def render_maintenance_tab(registry_utils):
    """メンテナンスタブをレンダリング"""
    st.subheader("メンテナンス機能")
    
    # レジストリ内容の直接確認
    render_registry_content_section(registry_utils)
    
    st.markdown("---")
    
    # 空ディレクトリの確認
    render_empty_directories_section(registry_utils)

def render_registry_content_section(registry_utils):
    """レジストリ内容表示セクション"""
    st.markdown("**レジストリ内容の直接確認**")
    st.write("レジストリファイルの生データを確認できます")
    
    if st.checkbox("レジストリファイルの内容を表示", key="show_registry"):
        try:
            registry = registry_utils.template_manager.load_registry()
            if registry:
                st.json(registry)
            else:
                st.info("レジストリが空です")
        except Exception as e:
            st.error(f"レジストリ読み込みエラー: {str(e)}")

def render_empty_directories_section(registry_utils):
    """空ディレクトリ確認セクション"""
    st.markdown("**空ディレクトリのクリーンアップ**")
    st.write("使用されていない裁判所ディレクトリを確認できます")
    
    empty_dirs = registry_utils.get_empty_directories()
    
    if empty_dirs:
        st.warning(f"テンプレートが登録されていない裁判所: {len(empty_dirs)}件")
        
        # 詳細表示
        with st.expander("詳細を表示"):
            for empty_dir in empty_dirs:
                st.text(f"- {empty_dir}")
        
        # クリーンアップ提案
        st.info("これらのディレクトリは手動で削除するか、テンプレートを追加することを検討してください")
    else:
        st.success("すべての裁判所ディレクトリが使用されています")