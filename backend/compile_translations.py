"""
翻訳ファイル（.po）を .mo にコンパイル

Usage:
    python compile_translations.py

Requirements:
    - gettext (推奨): winget install GnuWin32.GetText
    - polib (代替): pip install polib
"""

import subprocess
from pathlib import Path


def compile_with_msgfmt(po_file, mo_file):
    """msgfmt を使用してコンパイル"""
    result = subprocess.run(
        ["msgfmt", "-o", mo_file, po_file], capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"✅ {mo_file}")
    else:
        raise FileNotFoundError("msgfmt not found")


def compile_with_polib(po_file, mo_file):
    """polib を使用してコンパイル（代替手段）"""
    try:
        import polib

        po = polib.pofile(str(po_file))
        po.save_as_mofile(str(mo_file))
        print(f"✅ {mo_file} (polib)")
    except ImportError:
        print("❌ polib がインストールされていません: pip install polib")


def main():
    """すべての .po ファイルをコンパイル"""
    BASE_DIR = Path(__file__).resolve().parent
    LOCALE_DIR = BASE_DIR / "locale"

    if not LOCALE_DIR.exists():
        print(f"❌ locale ディレクトリが見つかりません")
        return

    po_files = list(LOCALE_DIR.glob("**/LC_MESSAGES/django.po"))

    if not po_files:
        print("⚠️ .po ファイルが見つかりません")
        return

    print(f"📁 {len(po_files)} 個のファイルを処理中...\n")

    for po_file in po_files:
        mo_file = po_file.with_suffix(".mo")

        try:
            compile_with_msgfmt(po_file, mo_file)
        except FileNotFoundError:
            print("⚠️ gettext が見つかりません。polib を使用します。")
            compile_with_polib(po_file, mo_file)

    print("\n✅ コンパイル完了")


if __name__ == "__main__":
    main()
