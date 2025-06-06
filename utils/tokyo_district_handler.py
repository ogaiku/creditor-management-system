class TokyoDistrictHandler:
    """東京地裁専用の処理を行うクラス"""
    
    def __init__(self):
        pass
    
    def is_tokyo_district_bankruptcy(self, court_name, procedure_type):
        """東京地裁の自己破産かどうか判定"""
        return court_name == "東京地方裁判所" and procedure_type == "自己破産"
    
    def convert_claim_name_to_code(self, claim_name):
        """東京地裁用：債権名をコードに変換"""
        claim_name_str = str(claim_name).strip()
        conversion_map = {
            '貸付金': 'A',
            '立替金': 'B', 
            '保証金': 'C',
            'その他': 'D'
        }
        return conversion_map.get(claim_name_str, 'D')  # 該当なしの場合はDを返す
    
    def replace_tokyo_variables(self, text, creditor_data):
        """東京地裁自己破産用のA/B変数置換（修正版）"""
        result = text
        creditor_count = len(creditor_data)
        
        
        # ページ構成の計算
        if creditor_count <= 8:
            # 1～8人：最終頁用のみ
            general_count = 0
            final_count = creditor_count
            
        else:
            # 9人以上：一般用を7人単位で使い、残りを最終頁用に
            remainder = creditor_count % 7
            if remainder == 0:
                final_count = 7
            else:
                final_count = remainder
            
            if final_count > 8:
                final_count = final_count - 7
            
            general_count = creditor_count - final_count
        
        
        # A系変数（最終頁用）の処理
        final_start = general_count + 1
        
        for i in range(1, 9):  # A1～A8
            if i <= final_count:
                creditor_index = final_start + i - 2  # 実際の債権者インデックス（0ベース）
                
                
                if creditor_index >= 0 and creditor_index < len(creditor_data):
                    creditor = creditor_data[creditor_index]
                    claim_name_code = self.convert_claim_name_to_code(creditor.get('債権名', ''))
                    
                    replacements = {
                        f"{{company_name_A{i}}}": str(creditor.get('会社名', '')),
                        f"{{branch_name_A{i}}}": str(creditor.get('支店名', '')),
                        f"{{postal_code_A{i}}}": str(creditor.get('郵便番号', '')),
                        f"{{address_A{i}}}": str(creditor.get('住所', '')),
                        f"{{phone_number_A{i}}}": str(creditor.get('電話番号', '')),
                        f"{{fax_number_A{i}}}": str(creditor.get('FAX番号', '')),
                        f"{{claim_name_A{i}}}": claim_name_code,
                        f"{{claim_amount_A{i}}}": str(creditor.get('債権額', '')),
                        f"{{contract_date_A{i}}}": str(creditor.get('契約日', '')),
                        f"{{first_borrowing_date_A{i}}}": str(creditor.get('初回借入日', '')),
                        f"{{last_borrowing_date_A{i}}}": str(creditor.get('最終借入日', '')),
                        f"{{last_payment_date_A{i}}}": str(creditor.get('最終返済日', '')),
                        f"{{original_creditor_A{i}}}": str(creditor.get('原債権者', '')),
                        f"{{substitution_or_transfer_A{i}}}": str(creditor.get('代位弁済/債権譲渡', '')),
                        f"{{transfer_date_A{i}}}": str(creditor.get('債権移転日', '')),
                        f"{{status_A{i}}}": str(creditor.get('ステータス', '')),
                        f"{{notes_A{i}}}": str(creditor.get('備考', '')),
                        f"{{registration_date_A{i}}}": str(creditor.get('登録日', '')),
                        f"{{creditor_rank_A{i}}}": str(creditor_index + 1),  # 1ベースで表示
                        f"{{id_A{i}}}": str(creditor.get('ID', ''))
                    }
                    
                    
                    for var, value in replacements.items():
                        if var in result:
                            result = result.replace(var, value)
            
            # 使用していないA系変数を空文字で置換
            if i > final_count:
                empty_replacements = {
                    f"{{company_name_A{i}}}": "",
                    f"{{branch_name_A{i}}}": "",
                    f"{{postal_code_A{i}}}": "",
                    f"{{address_A{i}}}": "",
                    f"{{phone_number_A{i}}}": "",
                    f"{{fax_number_A{i}}}": "",
                    f"{{claim_name_A{i}}}": "",
                    f"{{claim_amount_A{i}}}": "",
                    f"{{contract_date_A{i}}}": "",
                    f"{{first_borrowing_date_A{i}}}": "",
                    f"{{last_borrowing_date_A{i}}}": "",
                    f"{{last_payment_date_A{i}}}": "",
                    f"{{original_creditor_A{i}}}": "",
                    f"{{substitution_or_transfer_A{i}}}": "",
                    f"{{transfer_date_A{i}}}": "",
                    f"{{status_A{i}}}": "",
                    f"{{notes_A{i}}}": "",
                    f"{{registration_date_A{i}}}": "",
                    f"{{creditor_rank_A{i}}}": "",
                    f"{{id_A{i}}}": ""
                }
                
                for var, value in empty_replacements.items():
                    result = result.replace(var, value)
        
        # B系変数（一般用）の処理
        if general_count > 0:
            for i in range(1, 22):  # B1～B21
                if i <= general_count:
                    creditor = creditor_data[i - 1]
                    claim_name_code = self.convert_claim_name_to_code(creditor.get('債権名', ''))
                    
                    replacements = {
                        f"{{company_name_B{i}}}": str(creditor.get('会社名', '')),
                        f"{{branch_name_B{i}}}": str(creditor.get('支店名', '')),
                        f"{{postal_code_B{i}}}": str(creditor.get('郵便番号', '')),
                        f"{{address_B{i}}}": str(creditor.get('住所', '')),
                        f"{{phone_number_B{i}}}": str(creditor.get('電話番号', '')),
                        f"{{fax_number_B{i}}}": str(creditor.get('FAX番号', '')),
                        f"{{claim_name_B{i}}}": claim_name_code,
                        f"{{claim_amount_B{i}}}": str(creditor.get('債権額', '')),
                        f"{{contract_date_B{i}}}": str(creditor.get('契約日', '')),
                        f"{{first_borrowing_date_B{i}}}": str(creditor.get('初回借入日', '')),
                        f"{{last_borrowing_date_B{i}}}": str(creditor.get('最終借入日', '')),
                        f"{{last_payment_date_B{i}}}": str(creditor.get('最終返済日', '')),
                        f"{{original_creditor_B{i}}}": str(creditor.get('原債権者', '')),
                        f"{{substitution_or_transfer_B{i}}}": str(creditor.get('代位弁済/債権譲渡', '')),
                        f"{{transfer_date_B{i}}}": str(creditor.get('債権移転日', '')),
                        f"{{status_B{i}}}": str(creditor.get('ステータス', '')),
                        f"{{notes_B{i}}}": str(creditor.get('備考', '')),
                        f"{{registration_date_B{i}}}": str(creditor.get('登録日', '')),
                        f"{{creditor_rank_B{i}}}": str(i),
                        f"{{id_B{i}}}": str(creditor.get('ID', ''))
                    }
                    
                    for var, value in replacements.items():
                        result = result.replace(var, value)
                
                # 使用していないB系変数を空文字で置換
                if i > general_count:
                    empty_replacements = {
                        f"{{company_name_B{i}}}": "",
                        f"{{branch_name_B{i}}}": "",
                        f"{{postal_code_B{i}}}": "",
                        f"{{address_B{i}}}": "",
                        f"{{phone_number_B{i}}}": "",
                        f"{{fax_number_B{i}}}": "",
                        f"{{claim_name_B{i}}}": "",
                        f"{{claim_amount_B{i}}}": "",
                        f"{{contract_date_B{i}}}": "",
                        f"{{first_borrowing_date_B{i}}}": "",
                        f"{{last_borrowing_date_B{i}}}": "",
                        f"{{last_payment_date_B{i}}}": "",
                        f"{{original_creditor_B{i}}}": "",
                        f"{{substitution_or_transfer_B{i}}}": "",
                        f"{{transfer_date_B{i}}}": "",
                        f"{{status_B{i}}}": "",
                        f"{{notes_B{i}}}": "",
                        f"{{registration_date_B{i}}}": "",
                        f"{{creditor_rank_B{i}}}": "",
                        f"{{id_B{i}}}": ""
                    }
                    
                    for var, value in empty_replacements.items():
                        result = result.replace(var, value)
        else:
            # 最終頁のみの場合、B系変数を全て空文字で置換
            for i in range(1, 22):
                empty_replacements = {
                    f"{{company_name_B{i}}}": "",
                    f"{{branch_name_B{i}}}": "",
                    f"{{postal_code_B{i}}}": "",
                    f"{{address_B{i}}}": "",
                    f"{{phone_number_B{i}}}": "",
                    f"{{fax_number_B{i}}}": "",
                    f"{{claim_name_B{i}}}": "",
                    f"{{claim_amount_B{i}}}": "",
                    f"{{contract_date_B{i}}}": "",
                    f"{{first_borrowing_date_B{i}}}": "",
                    f"{{last_borrowing_date_B{i}}}": "",
                    f"{{last_payment_date_B{i}}}": "",
                    f"{{original_creditor_B{i}}}": "",
                    f"{{substitution_or_transfer_B{i}}}": "",
                    f"{{transfer_date_B{i}}}": "",
                    f"{{status_B{i}}}": "",
                    f"{{notes_B{i}}}": "",
                    f"{{registration_date_B{i}}}": "",
                    f"{{creditor_rank_B{i}}}": "",
                    f"{{id_B{i}}}": ""
                }
                
                for var, value in empty_replacements.items():
                    result = result.replace(var, value)
        
        return result