"""
アプリケーションのデザインとスタイル定義
"""

# メインCSS
MAIN_CSS = """
<style>
    /* ベース設定 */
    .main {
        background-color: #fefefe;
        padding: 1rem;
    }
    
    /* カードデザイン */
    .spreadsheet-card {
        background-color: #fcfcff;
        border: 1px solid #e6e9f0;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        transition: box-shadow 0.2s ease;
    }
    
    .spreadsheet-card:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* URL表示ボックス */
    .url-box {
        background-color: #f8f9fb;
        border: 1px solid #e6e9f0;
        border-radius: 8px;
        padding: 0.6rem;
        font-family: monospace;
        font-size: 0.9rem;
        word-break: break-all;
        color: #4a5568;
    }
    
    /* ステータスバッジ */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-connected {
        background-color: #e8f5e8;
        color: #2d5a2d;
        border: 1px solid #c8e6c8;
    }
    
    .status-error {
        background-color: #ffeaea;
        color: #8b2635;
        border: 1px solid #f5c2c7;
    }
    
    /* ボタンスタイル - パステルカラー（全ボタンタイプ対応）*/
    .stButton > button,
    .stFormSubmitButton > button,
    button[data-testid="baseButton-primary"],
    button[data-testid="baseButton-secondary"],
    div[data-testid="stFormSubmitButton"] > button,
    .stForm button[kind="primary"],
    .stForm button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        border: 1px solid #e2e5ea !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1rem !important;
        min-height: 2.4rem !important;
        background-color: #f7f8fc !important;
        color: #4a5568 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    .stForm button:hover {
        background-color: #f0f2f7 !important;
        border-color: #c4c9d4 !important;
    }
    
    /* 登録ボタン（プライマリ）- パステルグリーン - 最優先 */
    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    button[data-testid="baseButton-primary"],
    div[data-testid="stFormSubmitButton"] > button,
    .stForm button[kind="primary"],
    .stForm > div > div > div > button,
    form button[type="submit"] {
        background-color: #a8d5a8 !important;
        color: #2d5a2d !important;
        border-color: #a8d5a8 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        min-height: 2.8rem !important;
        width: 100% !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stFormSubmitButton > button[kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    .stForm button[kind="primary"]:hover,
    .stForm > div > div > div > button:hover,
    form button[type="submit"]:hover {
        background-color: #98c798 !important;
        border-color: #98c798 !important;
        color: #2d5a2d !important;
    }
    
    /* 削除ボタン（セカンダリ）- パステルグレー */
    .stButton > button[kind="secondary"],
    .stFormSubmitButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background-color: #c4c9d4 !important;
        color: #4a5568 !important;
        border-color: #c4c9d4 !important;
        font-weight: 500 !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    .stFormSubmitButton > button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background-color: #b4b9c4 !important;
        border-color: #b4b9c4 !important;
    }
    
    /* フォームコンテナ内のボタン全体に適用 */
    .stForm button,
    .stForm input[type="submit"],
    .stForm [role="button"] {
        background-color: #a8d5a8 !important;
        color: #2d5a2d !important;
        border-color: #a8d5a8 !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        min-height: 2.8rem !important;
        width: 100% !important;
        border: 1px solid #a8d5a8 !important;
    }
    
    .stForm button:hover,
    .stForm input[type="submit"]:hover,
    .stForm [role="button"]:hover {
        background-color: #98c798 !important;
        border-color: #98c798 !important;
        color: #2d5a2d !important;
    }
    
    /* テキストスタイル */
    .card-header {
        color: #3d4852;
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .card-subtitle {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    
    /* メッセージボックス - パステルカラー */
    .info-box {
        background-color: #f0f4ff;
        border: 1px solid #c4d3ff;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #3d4c7a;
    }
    
    .success-box {
        background-color: #f0f9f0;
        border: 1px solid #c8e6c8;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        color: #2d5a2d;
        font-weight: 500;
    }
    
    .warning-box {
        background-color: #fff8e7;
        border: 1px solid #f5d982;
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        color: #8b6914;
        font-weight: 500;
    }
    
    /* フォーム要素 - パステルカラー */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e5ea;
        background-color: #fcfcff;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 1px solid #e2e5ea;
        background-color: #fcfcff;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1px solid #e2e5ea;
        background-color: #fcfcff;
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
        border-top: 1px solid #e6e9f0;
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

# フッタースタイル - より淡い色
FOOTER_HTML = """
<div style="text-align: center; color: #9ca3af; padding: 1rem; background-color: #fafbfc; border-top: 1px solid #f0f2f5; margin-top: 2rem; border-radius: 8px;">
    <small>
        <strong>債権者データ管理システム</strong><br>
        効率的な債権者情報管理
    </small>
</div>
"""

# シンプルなボタンHTML - より淡い色（サイズ統一）
def get_button_html(url, text, color="#f0f9f0"):
    return f"""
    <a href="{url}" target="_blank" style="text-decoration: none;">
        <button style="
            width: 100%; 
            padding: 0.6rem 1rem; 
            background-color: {color}; 
            color: #4a6741; 
            border: 1px solid #e6f4e6; 
            border-radius: 8px; 
            cursor: pointer; 
            font-weight: 500;
            font-size: 0.95rem;
            min-height: 2.4rem;
            box-sizing: border-box;
        ">
            {text}
        </button>
    </a>
    """

# 緑色のボタン（既存の関数名を維持）- より淡いグリーン
def get_green_button_html(url, text):
    return get_button_html(url, text, "#f0f9f0")

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