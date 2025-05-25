import streamlit as st
import sys
import os
import json

# パス設定
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.template_manager import TemplateManager
from utils.styles import MAIN_CSS

# CSS適用
st.markdown(MAIN_CSS, unsafe_allow_html=True)

st.title("テンプレートレジストリ管理")

@st.cache_resource
def get_template_manager():
    return TemplateManager()

template_manager = get_template_manager()

# タブ構成
tab1, tab2, tab3, tab4 = st.tabs(["レジストリ情報", "レジストリ操作", "移行・修復", "バックアップ"])

# レジストリ情報タブ
with tab1:
    st.subheader("現在のレジストリ情報")
    
    try:
        registry_info = template_manager.get_registry_info()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("登録裁判所数", registry_info["total_courts"])
        with col2:
            st.metric("総テンプレート数", registry_info["total_templates"])
        with col3:
            st.metric("利用可能テンプレート", len(template_manager.list_available_templates()))
        
        st.markdown("---")
        st.subheader("裁判所別テンプレート詳細")
        
        if registry_info["courts"]:
            for court_info in registry_info["courts"]:
                with st.expander(f"{court_info['name']} ({len(court_info['procedures'])}件)"):
                    if court_info['procedures']:
                        for procedure in court_info['procedures']:
                            template_key = f"{court_info['name']}_{procedure}" if procedure != "従来形式" else court_info['name']
                            template_info = template_manager.get_template_info(template_key)
                            
                            if template_info:
                                st.write(f"**{procedure}**")
                                st.write(f"- 説明: {template_info.get('description', 'なし')}")
                                st.write(f"- 作成日: {template_info.get('created_date', 'なし')}")
                                st.write(f"- 最終更新: {template_info.get('last_modified', 'なし')}")
                                st.write(f"- ファイルパス: {template_info.get('file_path', 'なし')}")
                                st.write("")
                    else:
                        st.write("テンプレートがありません")
        else:
            st.info("登録されているテンプレートはありません")
    
    except Exception as e:
        st.error(f"レジストリ情報取得エラー: {e}")

# レジストリ操作タブ
with tab2:
    st.subheader("レジストリ操作")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**レジストリリセット**")
        st.write("レジストリファイルを完全に削除して初期化します")
        
        if st.button("レジストリをリセット", type="secondary"):
            if st.session_state.get('confirm_reset', False):
                template_manager.reset_registry()
                st.session_state.confirm_reset = False
                st.rerun()
            else:
                st.session_state.confirm_reset = True
                st.warning("もう一度クリックすると実行されます")
    
    with col2:
        st.write("**レジストリ再構築**")
        st.write("ファイルシステムを走査してレジストリを再構築します")
        
        if st.button("レジストリを再構築", type="primary"):
            with st.spinner("レジストリを再構築中..."):
                template_manager.rebuild_registry()
                st.cache_resource.clear()
                st.rerun()

# 移行・修復タブ
with tab3:
    st.subheader("データ移行・修復")
    
    st.write("**従来形式から新形式への移行**")
    st.write("裁判所名のみのテンプレートを個人再生・自己破産の両方にコピーします")
    
    if st.button("従来形式テンプレートを移行", type="primary"):
        with st.spinner("テンプレートを移行中..."):
            migrated = template_manager.migrate_old_templates()
            
            if migrated:
                st.success("移行が完了しました")
                st.cache_resource.clear()
                st.rerun()
            else:
                st.info("移行する従来形式のテンプレートはありませんでした")
    
    st.markdown("---")
    
    st.write("**レジストリ内容の直接確認**")
    if st.checkbox("レジストリファイルの内容を表示"):
        try:
            registry = template_manager.load_registry()
            st.json(registry)
        except Exception as e:
            st.error(f"レジストリ読み込みエラー: {e}")

# バックアップタブ
with tab4:
    st.subheader("バックアップ管理")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**バックアップ作成**")
        if st.button("現在のレジストリをバックアップ", type="primary"):
            backup_file = template_manager.backup_registry()
            if backup_file:
                st.success(f"バックアップを作成しました")
                st.code(backup_file)
    
    with col2:
        st.write("**バックアップファイル一覧**")
        try:
            template_dir = template_manager.base_path
            backup_files = []
            
            if os.path.exists(template_dir):
                for file in os.listdir(template_dir):
                    if file.startswith("template_registry.json.backup_"):
                        backup_files.append(file)
            
            if backup_files:
                backup_files.sort(reverse=True)  # 新しい順
                for backup_file in backup_files[:5]:  # 最新5件表示
                    st.text(backup_file)
            else:
                st.info("バックアップファイルはありません")
        
        except Exception as e:
            st.error(f"バックアップファイル一覧取得エラー: {e}")

# 使用方法
st.markdown("---")
st.subheader("使用方法")
st.markdown("""
**レジストリ管理の手順:**

1. **レジストリ情報**: 現在の状態を確認
2. **移行実行**: 従来形式のテンプレートがある場合は移行
3. **レジストリ再構築**: ファイルとレジストリの整合性を確保
4. **バックアップ**: 重要な変更前にバックアップを作成

**トラブルシューティング:**
- テンプレートが表示されない → レジストリ再構築を実行
- 従来形式のテンプレートがある → 移行を実行
- レジストリが破損した → バックアップから復元またはリセット
""")
