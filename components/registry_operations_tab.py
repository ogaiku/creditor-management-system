import streamlit as st

def render_registry_operations_tab(registry_utils):
    """レジストリ操作タブをレンダリング"""
    st.subheader("レジストリ操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_reset_section(registry_utils)
    
    with col2:
        render_rebuild_section(registry_utils)

def render_reset_section(registry_utils):
    """レジストリリセットセクション"""
    st.markdown("**レジストリリセット**")
    st.write("レジストリファイルを完全に削除して初期化します")
    st.warning("注意: この操作は元に戻すことができません")
    
    if st.button("レジストリをリセット", type="secondary", key="reset_btn"):
        if st.session_state.get('confirm_reset', False):
            def reset_operation():
                return registry_utils.template_manager.reset_registry()
            
            result = registry_utils.safe_operation("レジストリリセット", reset_operation)
            if result:
                st.success("レジストリをリセットしました")
            st.session_state.confirm_reset = False
            st.rerun()
        else:
            st.session_state.confirm_reset = True
            st.warning("もう一度クリックすると実行されます")

def render_rebuild_section(registry_utils):
    """レジストリ再構築セクション"""
    st.markdown("**レジストリ再構築**")
    st.write("ファイルシステムを走査してレジストリを再構築します")
    st.info("テンプレートが表示されない場合に実行してください")
    
    if st.button("レジストリを再構築", type="primary", key="rebuild_btn"):
        def rebuild_operation():
            return registry_utils.template_manager.rebuild_registry()
        
        result = registry_utils.safe_operation("レジストリ再構築", rebuild_operation)
        if result:
            st.success("レジストリを再構築しました")
            st.rerun()