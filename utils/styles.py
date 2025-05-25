"""
アプリケーションのデザインとスタイル定義
"""

# メインCSS
MAIN_CSS = """
<style>
    /* ベース設定 */
    .main {
        background-color: #ffffff;
        padding: 1rem;
    }
    
    /* カードデザイン */
    .spreadsheet-card {
        background-color: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.2s ease;
    }
    
    .spreadsheet-card:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* URL表示ボックス */
    .url-box {
        background-color: #f5f5f5;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 0.6rem;
        font-family: monospace;
        font-size: 0.9rem;
        word-break: break-all;
        color: #333;
    }
    
    /* ステータスバッジ */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    /* ボタンスタイル */
    .stButton > button {
        border-radius: 4px;
        font-weight: 500;
        border: 1px solid #ddd;
        font-size: 1rem;
        padding: 0.7rem 1rem;
        min-height: 2.5rem;
        background-color: #ffffff;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa;
        border-color: #007bff;
    }
    
    /* 登録ボタン（プライマリ）*/
    .stButton > button[kind="primary"] {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
        font-weight: 600;
        font-size: 1.1rem;
        min-height: 3rem;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
    
    /* 削除ボタン（セカンダリ）*/
    .stButton > button[kind="secondary"] {
        background-color: #6c757d;
        color: white;
        border-color: #6c757d;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #545b62;
        border-color: #545b62;
    }
    
    /* テキストスタイル */
    .card-header {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .card-subtitle {
        color: #6c757d;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* メッセージボックス */
    .info-box {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        border-radius: 4px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #0c5460;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        color: #155724;
        font-weight: 500;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 4px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        color: #856404;
        font-weight: 500;
    }
    
    /* フォーム要素 */
    .stTextInput > div > div > input {
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 4px;
        border: 1px solid #ddd;
    }
    
    /* レスポンシブ対応 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        
        .spreadsheet-card {
            padding: 1rem;
        }
        
        .status-badge {
            font-size: 0.8rem;
            padding: 0.25rem 0.6rem;
        }
    }
    
    /* セクション区切り */
    .section-divider {
        border-top: 1px solid #e8e8e8;
        margin: 1.5rem 0;
    }
    
    /* コンパクトレイアウト */
    .compact-layout {
        margin: 0.5rem 0;
    }
    
    .compact-layout h3 {
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
</style>
"""

# フッタースタイル
FOOTER_HTML = """
<div style="text-align: center; color: #6c757d; padding: 1rem; background-color: #f8f9fa; border-top: 1px solid #e8e8e8; margin-top: 2rem;">
    <small>
        <strong>債権者データ管理システム</strong><br>
        効率的な債権者情報管理
    </small>
</div>
"""

# シンプルなボタンHTML
def get_button_html(url, text, color="#007bff"):
    return f"""
    <a href="{url}" target="_blank" style="text-decoration: none;">
        <button style="
            width: 100%; 
            padding: 0.6rem; 
            background-color: {color}; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-weight: 500;
            font-size: 0.9rem;
        ">
            {text}
        </button>
    </a>
    """

# 緑色のボタン（既存の関数名を維持）
def get_green_button_html(url, text):
    return get_button_html(url, text, "#28a745")

# メッセージスタイル関数
def get_success_html(message):
    return f'<div class="success-box">{message}</div>'

def get_info_html(message):
    return f'<div class="info-box">{message}</div>'

def get_warning_html(message):
    return f'<div class="warning-box">{message}</div>'

# カードヘッダー用関数
def get_card_header_html(title, subtitle=""):
    subtitle_html = f'<div class="card-subtitle">{subtitle}</div>' if subtitle else ""
    return f'<div class="card-header">{title}</div>{subtitle_html}'