from typing import Callable, List, Tuple

# duduction rule (as of 2024)
INCOME_RULES: List[Tuple[float, Callable[[int], int]]] = [
    (550_999, lambda s: 0),
    (1_618_999, lambda s: s - 550_000),
    (1_619_999, lambda s: 1_069_000),
    (1_621_999, lambda s: 1_070_000),
    (1_623_999, lambda s: 1_072_000),
    (1_627_999, lambda s: 1_074_000),
    (1_799_999, lambda s: ((s // 4_000) * 1000) * 2.4 - 100_000),
    (3_599_999, lambda s: ((s // 4_000) * 1000) * 2.8 - 80_000),
    (6_599_999, lambda s: ((s // 4_000) * 1000) * 3.2 - 440_000),
    (8_499_999, lambda s: s * 0.9 - 1_100_000),
    (float('inf'), lambda s: s - 1_950_000)
]

# UI の定数
UI_CONFIG = {
    'APP_TITLE': '年末調整計算ツール',
    'PDF_VIEWER_TITLE': 'PDF ビューワー',
    'MAX_ZOOM': 3.0,
    'MIN_ZOOM': 0.25,
    'ZOOM_FACTOR': 1.2
}

# エラーメッセージ
ERROR_MESSAGES = {
    'FILE_NOT_FOUND': 'PDF ファイルが見つかりません',
    'PERMISSION_DENIED': 'PDF ファイルにアクセスする権限がありません',
    'INVALID_INPUT': '数値を正しく入力してください (例: 250000)',
    'PDF_DROP_ERROR': 'PDF ファイルをドロップしてください',
    'UNEXPECTED_EROOR': 'PDF ファイルを読み込むときに予期せぬエラーが発生しました'
}

# ラベルテキスト
LABEL_TEXTS = {
    'MONTHLY_SALARY': '月額給与 (円)',
    'BONUS1': '賞与1 (円)',
    'BONUS2': '賞与2 (円)',
    'TOTAL_YEARLY_SALARY': '年間給与金額: ',
    'INCOME_AMOUNT': '給与所得金額: '
}

# ラジオボタンテキスト
RADIO_BUTTON_TEXTS = {
    'SINGLE': '1年同一月給',
    'MONTHLY': '月毎に月給を入力する'
}

# ボタンテキスト
BUTTON_TEXTS = {
    'CALCULATE': '計算',
    'CLEAR': 'クリア',
    'SELECT_PDF': 'PDF を選択',
    'PREV_PAGE': '<<',
    'NEXT_PAGE': '>>',
    'ZOOM_IN': '+',
    'ZOOM_OUT': '-'
}
