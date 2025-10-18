# backend/compile_translations.py
"""
手動で .po ファイルを .mo ファイルにコンパイルするスクリプト

使い方:
python compile_translations.py
"""

import os
from pathlib import Path


def compile_po_to_mo(po_file_path):
    """
    .po ファイルを .mo ファイルにコンパイル
    
    引数:
        po_file_path: .po ファイルのパス
    """
    # .mo ファイルのパスを生成
    mo_file_path = po_file_path.replace('.po', '.mo')
    
    # msgfmt コマンドを実行（gettext がインストールされている場合）
    try:
        import subprocess
        result = subprocess.run(
            ['msgfmt', '-o', mo_file_path, po_file_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f'✅ コンパイル成功: {mo_file_path}')
        else:
            print(f'❌ コンパイル失敗: {result.stderr}')
            raise Exception('msgfmt が見つかりません')
    
    except FileNotFoundError:
        # gettext がインストールされていない場合
        print('⚠️  gettext が見つかりません。Python の polib を使用します。')
        compile_with_polib(po_file_path, mo_file_path)


def compile_with_polib(po_file_path, mo_file_path):
    """
    polib を使って .po を .mo にコンパイル
    
    gettext がインストールされていない場合の代替方法
    """
    try:
        import polib
    except ImportError:
        print('❌ polib がインストールされていません。')
        print('📦 インストール方法: pip install polib')
        return
    
    # .po ファイルを読み込み
    po = polib.pofile(po_file_path)
    
    # .mo ファイルに保存
    po.save_as_mofile(mo_file_path)
    
    print(f'✅ コンパイル成功（polib使用）: {mo_file_path}')


def main():
    """すべての .po ファイルをコンパイル"""
    
    # プロジェクトのルートディレクトリ
    BASE_DIR = Path(__file__).resolve().parent
    LOCALE_DIR = BASE_DIR / 'locale'
    
    if not LOCALE_DIR.exists():
        print(f'❌ locale ディレクトリが見つかりません: {LOCALE_DIR}')
        return
    
    # すべての .po ファイルを検索
    po_files = list(LOCALE_DIR.glob('**/LC_MESSAGES/django.po'))
    
    if not po_files:
        print('⚠️  .po ファイルが見つかりません')
        return
    
    print(f'📁 {len(po_files)} 個の .po ファイルが見つかりました\n')
    
    # 各 .po ファイルをコンパイル
    for po_file in po_files:
        print(f'🔄 コンパイル中: {po_file}')
        compile_po_to_mo(str(po_file))
    
    print('\n✅ すべての翻訳ファイルのコンパイルが完了しました')


if __name__ == '__main__':
    main()

    # ==================== 使い方 ====================
"""
翻訳ファイル（.po）を手動でコンパイルするスクリプト

使い方:
    python compile_translations.py

必要なツール:
    方法1: gettext（推奨）
        winget install GnuWin32.GetText
        python manage.py compilemessages
    
    方法2: polib（gettext なし）
        pip install polib
        python compile_translations.py
"""