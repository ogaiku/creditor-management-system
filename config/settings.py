"""
アプリケーション設定
"""

# アプリケーション設定
APP_CONFIG = {
    "page_title": "債権者データ管理システム",
    "layout": "wide"
}

# Google Sheets設定
GOOGLE_SHEETS_SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# データフィールド定義
CREDITOR_FIELDS = [
    'ID', '債務者名', '会社名', '支店名', '郵便番号', '住所',
    '電話番号', 'FAX番号', '債権名', '債権額', '契約日',
    '初回借入日', '最終借入日', '最終返済日', '原債権者',
    '代位弁済/債権譲渡', '債権移転日', 'ステータス', '備考', '登録日'
]

# JSONサンプル
JSON_SAMPLE = """{
  "debtor_name": "株式会社サンプル",
  "company_name": "○○ファイナンス株式会社",
  "branch_name": "",
  "postal_code": "〒123-4567",
  "address": "東京都港区赤坂1-2-3",
  "phone_number": "03-1234-5678",
  "fax_number": "03-1234-5679",
  "claim_name": "貸付金",
  "claim_amount": "3000000",
  "contract_date": "2024年01月15日",
  "first_borrowing_date": "2024年01月16日",
  "last_borrowing_date": "2024年03月01日",
  "last_payment_date": "2024年04月30日",
  "original_creditor": "○○信用組合",
  "substitution_or_transfer": "債権譲渡",
  "transfer_date": "2024年05月01日"
}"""
