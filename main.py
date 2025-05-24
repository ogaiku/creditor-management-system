# main.py
"""
債権者データ管理システム - メインアプリケーション
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.settings import APP_CONFIG, STATUS_OPTIONS
from utils.database_helper import init_database, get_statistics
from pages.dashboard import show_dashboard
from pages.data_management import show_data_management
from pages.template_input import show_template_input

def main():
    """メインアプリケーション"""
    
    # ページ設定
    st.set_page_config(**APP_CONFIG)
    
    # データベース初期化
    init_database()
    
    # カスタムCSS
    st.markdown("""
    <style>
    .main-header {
        color: #1f77b4;
        font-size: 2.0rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    
    .sidebar-metric {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        border-left: 3px solid #1f77b4;
    }
    
    .metric-value {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #666;
    }
    
    .status-pending { color: #ffc107; }
    .status-verified { color: #28a745; }
    .status-converted { color: #17a2b8; }
    </style>
    """, unsafe_allow_html=True)
    
    # ヘッダー
    st.markdown('<h1 class="main-header">債権者データ管理システム</h1>', unsafe_allow_html=True)
    
    # サイドバー
    with st.sidebar:
        st.title("メニュー")
        
        # 統計情報の表示
        try:
            stats = get_statistics()
            
            st.markdown("### データ概要")
            
            # 総件数
            st.markdown(f"""
            <div class="sidebar-metric">
                <div class="metric-value">{stats['total_count']}</div>
                <div class="metric-label">総データ数</div>
            </div>
            """, unsafe_allow_html=True)
            
            # ステータス別件数
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="sidebar-metric">
                    <div class="metric-value status-pending">{stats['pending_count']}</div>
                    <div class="metric-label">未確認</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="sidebar-metric">
                    <div class="metric-value status-converted">{stats['converted_count']}</div>
                    <div class="metric-label">変換済み</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="sidebar-metric">
                    <div class="metric-value status-verified">{stats['verified_count']}</div>
                    <div class="metric-label">確認済み</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="sidebar-metric">
                    <div class="metric-value">{stats['today_count']}</div>
                    <div class="metric-label">今日の登録</div>
                </div>
                """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"統計情報の取得に失敗しました: {e}")
        
        st.markdown("---")
        
        # メニュー選択
        menu = st.radio(
            "機能を選択してください",
            [
                "ダッシュボード",
                "データ管理", 
                "裁判所書式作成"
            ]
        )
    
    # メイン画面表示
    if menu == "ダッシュボード":
        show_dashboard()
    elif menu == "データ管理":
        show_data_management()
    elif menu == "裁判所書式作成":
        show_template_input()

if __name__ == "__main__":
    main()
