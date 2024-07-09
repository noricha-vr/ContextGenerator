import fnmatch
from collections import defaultdict
from pathlib import Path
import platform
import subprocess
from config import EXCLUDE_FILES

def is_windows():
    """
    現在のシステムがWindowsかどうかを判定する関数

    Returns:
        bool: システムがWindowsの場合はTrue、それ以外の場合はFalse
    """
    return platform.system().lower() == "windows"


def format_number_with_commas(number):
    """
    数値をコンマ区切りの文字列に変換する関数

    :param number: 整数または浮動小数点数
    :return: コンマ区切りの文字列
    """
    return f"{number:,}"

def generate_summary(root_dir: Path, exclude_dirs: list[str], include_extensions: list[str], output_file: str,
                     output_dir: Path, target_files: list[str]):
    """
    指定されたディレクトリ内のファイルをマークダウン形式で出力する。

    Args:
        root_dir: ルートディレクトリ
        exclude_dirs: 除外するディレクトリリスト
        include_extensions: 含めるファイル拡張子リスト
        output_file: 出力ファイル名
        output_dir: 出力フォルダ
        target_files: 取得対象のファイル名リスト

    Returns:
        tuple: ファイル統計情報と合計文字数
    """

    # ディレクトリ構造を tree コマンドで取得
    exclude_pattern = "|".join(exclude_dirs + ["__pycache__", "*.pyc"])
    tree_output = subprocess.check_output(
        ["tree", "-N", "-L", "4", "-I", exclude_pattern, str(root_dir)], encoding='utf-8')

    # ファイル情報を取得
    file_paths = []
    for path in root_dir.rglob('*'):
        if path.is_file():
            relative_path = path.relative_to(root_dir)
            if not any(part in exclude_dirs for part in relative_path.parts):
                if any(fnmatch.fnmatch(path.name, pattern) for pattern in EXCLUDE_FILES):
                    print(f"Excluded: {path}")
                    continue

                if path.suffix in include_extensions or path.name in target_files:
                    file_paths.append(path)

    print(f'Selected files: {file_paths}')

    # ファイル統計情報の初期化
    file_stats = defaultdict(lambda: {'count': 0,'chars': 0})
    total_chars = 0

    # マークダウン形式で出力
    output_content = f"""
## ディレクトリ構造

{tree_output}

## ファイル一覧

"""

    for file_path in file_paths:
        # ファイルを開いて中身を取得
        try:
            file_content = file_path.read_text(encoding='utf-8')
            # ファイル統計情報の更新
            extension = file_path.suffix
            file_stats[extension]['count'] += 1
            file_stats[extension]['chars'] += len(file_content)
            total_chars += len(file_content)

        except UnicodeDecodeError:
            print(f"UnicodeDecodeError: {file_path}")
            continue

        output_content += f"""
```{file_path.relative_to(root_dir)}
{file_content.replace("```", "``````")}
"""
    # ファイル出力
    output_path = output_dir / output_file
    output_path.write_text(output_content, encoding='utf-8')

    return file_stats, format_number_with_commas(total_chars)

if __name__ == '__main__':
    root_dir = Path("./")  # ルートディレクトリを指定
    exclude_dirs = [".venv", ".git"]  # 除外するディレクトリ
    include_extensions = [".md", ".yaml", ".yml",
    ".txt", ".py", ".html"]  # 含めるファイル拡張子
    output_file = "summary.md"
    output_dir = Path.home() / "Desktop"  # 出力フォルダを指定
    target_files = ["README.md", "requirements.txt",
    "config.yaml", "Dockerfile"]  # 取得対象のファイル名を指定
    file_stats = generate_summary(root_dir, exclude_dirs, include_extensions,
    output_file, output_dir, target_files)
    print("Summary generated successfully!")
    print("File statistics:")
    for ext, stats in file_stats.items():
        print(f"{ext}: {stats['count']} files, {stats['lines']} lines")