# 裁判所と手続種別の選択肢
COURTS = [
    "東京地方裁判所",
    "大阪地方裁判所", 
    "名古屋地方裁判所",
    "横浜地方裁判所",
    "神戸地方裁判所",
    "福岡地方裁判所",
    "仙台地方裁判所",
    "広島地方裁判所",
    "札幌地方裁判所",
    "その他"
]

PROCEDURE_TYPES = ["個人再生", "自己破産"]

# テンプレート変数の定義
TEMPLATE_VARIABLES = {
    "債務者情報": {
        "{debtor_name}": "債務者名",
        "{court_name}": "裁判所名",
        "{case_number}": "事件番号",
        "{procedure_type}": "手続種別（個人再生/自己破産）",
        "{today}": "今日の日付（YYYY年MM月DD日）",
        "{today_slash}": "今日の日付（YYYY/MM/DD）",
        "{total_creditors}": "債権者総数",
        "{total_claim_amount}": "債権金額総計"
    },
    "債権者情報（n=1,2,3...で番号指定）": {
        "{id_n}": "ID",
        "{company_name_n}": "会社名",
        "{branch_name_n}": "支店名", 
        "{postal_code_n}": "郵便番号",
        "{address_n}": "住所",
        "{phone_number_n}": "電話番号",
        "{fax_number_n}": "FAX番号",
        "{claim_name_n}": "債権名",
        "{claim_amount_n}": "債権額",
        "{contract_date_n}": "契約日",
        "{first_borrowing_date_n}": "初回借入日",
        "{last_borrowing_date_n}": "最終借入日", 
        "{last_payment_date_n}": "最終返済日",
        "{original_creditor_n}": "原債権者",
        "{substitution_or_transfer_n}": "代位弁済/債権譲渡",
        "{transfer_date_n}": "債権移転日",
        "{status_n}": "ステータス",
        "{notes_n}": "備考",
        "{registration_date_n}": "登録日"
    },
    "計算・集計": {
        "{sum_claim_amount_1_to_n}": "1番目からn番目までの債権額合計",
        "{creditor_rank_n}": "n番目の債権者順位（1,2,3...）"
    }
}