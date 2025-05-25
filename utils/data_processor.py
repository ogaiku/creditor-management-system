"""
データ処理ユーティリティ
"""

import json

def parse_json_data(json_text):
    """JSONデータをパースして検証"""
    try:
        data = json.loads(json_text)
        
        if isinstance(data, list):
            return data, None
        elif isinstance(data, dict):
            return [data], None
        else:
            return None, "JSONデータの形式が正しくありません"
    except json.JSONDecodeError as e:
        return None, f"JSON解析エラー: {str(e)}"

def validate_creditor_data(data):
    """債権者データの基本検証"""
    errors = []
    
    if not data.get('debtor_name', '').strip():
        errors.append("債務者名は必須です")
    
    return errors

def clean_data(data):
    """データのクリーニング"""
    cleaned = {}
    for key, value in data.items():
        if value is None:
            cleaned[key] = ''
        else:
            cleaned[key] = str(value).strip()
    return cleaned

def format_currency(amount):
    """通貨形式でフォーマット"""
    try:
        if amount is None or amount == "":
            return ""
        
        if isinstance(amount, str):
            amount = amount.replace(",", "").replace("円", "")
        
        num_amount = float(amount)
        return f"{num_amount:,.0f}円"
    except (ValueError, TypeError):
        return str(amount)
