import streamlit as st
import os

def render_backup_tab(registry_utils):
    """バックアップタブをレンダリング"""
    st.subheader("バックアップ管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_backup_creation_section(registry_utils)
    
    with col2:
        render_backup_list_section(registry_utils)

def render_backup_creation_section(registry_utils):
    """バックアップ作成セクション"""
    st.markdown("**バックアップ作成**")
    st.write("現在のレジストリ状態をバックアップファイルとして保存します")
    st.info("重要な変更を行う前にバックアップを作成することをお勧めします")
    
    if st.button("現在のレジストリをバックアップ", type="primary", key="backup_btn"):
        def backup_operation():
            return registry_utils.template_manager.backup_registry()
        
        backup_file = registry_utils.safe_operation("バックアップ作成", backup_operation)
        if backup_file:
            st.success("バックアップを作成しました")
            st.code(f"{os.path.basename(backup_file)}")

def render_backup_list_section(registry_utils):
    """バックアップファイル一覧セクション"""
    st.markdown("**バックアップファイル一覧**")
    
    backup_files = registry_utils.get_backup_files()
    
    if backup_files:
        st.write(f"バックアップファイル: {len(backup_files)}件")
        
        # 最新5件を表示
        display_count = min(5, len(backup_files))
        st.write(f"最新{display_count}件のバックアップ:")
        
        for i, backup in enumerate(backup_files[:display_count]):
            with st.container():
                st.text(f"{backup['name']}")
                st.caption(f"作成日時: {backup['time'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if i < display_count - 1:  # 最後の要素以外に区切り線
                    st.markdown("---")
        
        # 全件表示オプション
        if len(backup_files) > 5:
            with st.expander(f"すべてのバックアップを表示 ({len(backup_files)}件)"):
                for backup in backup_files:
                    st.text(f"{backup['name']}")
                    st.caption(f"{backup['time'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.info("バックアップファイルはありません")