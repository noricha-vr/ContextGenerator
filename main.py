import platform
import re
import fnmatch
from collections import defaultdict
from pathlib import Path
import subprocess
from typing import List, Dict, Tuple

from config import EXCLUDE_FILES
from logging_config import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


def generate_summary(root_dir: Path, exclude_dirs: List[str], include_extensions: List[str], output_file: str,
                     output_dir: Path, target_files: List[str]) -> Tuple[Dict[str, Dict[str, int]], str]:
    """
    サマリーを生成する

    Args:
        root_dir: ルートディレクトリ
        exclude_dirs: 除外するディレクトリリスト
        include_extensions: 含めるファイル拡張子リスト
        output_file: 出力ファイル名
        output_dir: 出力フォルダ
        target_files: 取得対象のファイル名リスト

    Returns:
        Tuple[Dict[str, Dict[str, int]], str]: ファイル統計情報と合計文字数
    """

    # ディレクトリ構造を取得
    directory_structure = get_directory_structure(root_dir, exclude_dirs)

    # ファイル収集
    file_paths = collect_files(root_dir, exclude_dirs, include_extensions, target_files)

    # ファイル統計計算
    file_stats, total_chars = calculate_file_stats(file_paths)

    # マークダウン出力生成
    output_content = generate_markdown_output(root_dir, file_paths, directory_structure)

    # ファイル出力
    output_path = output_dir / output_file
    output_path.write_text(output_content, encoding='utf-8')
    logger.info(f"Summary generated successfully: {output_path}")

    return file_stats, total_chars


def get_directory_structure(root_dir: Path, exclude_dirs: List[str]) -> str:
    """
    ディレクトリ構造を取得する関数

    Args:
        root_dir: ルートディレクトリ
        exclude_dirs: 除外するディレクトリリスト

    Returns:
        str: ディレクトリ構造の文字列表現
    """
    if is_windows():
        logger.warning("Windows環境では tree コマンドを使用しません。")
        return ""

    exclude_pattern = "|".join(exclude_dirs + ["__pycache__", "*.pyc"])
    try:
        tree_output = subprocess.check_output(
            ["tree", "-N", "-L", "4", "-I", exclude_pattern, str(root_dir)],
            encoding='utf-8'
        )
        if not tree_output:
            logger.warning("ディレクトリ構造が取得できませんでした。")
            return ""
        directory_structure = f"""## ディレクトリ構造\n\n```\n{tree_output}```\n\n"""
        return directory_structure
    except subprocess.CalledProcessError as e:
        logger.error(f"tree コマンドの実行中にエラーが発生しました treeをインストールしてください。: {e}")
        return ""


def collect_files(root_dir: Path, exclude_dirs: List[str], include_extensions: List[str], target_files: List[str]) -> \
List[Path]:
    """
    指定された条件に基づいてファイルを収集する

    Args:
        root_dir: ルートディレクトリ
        exclude_dirs: 除外するディレクトリリスト
        include_extensions: 含めるファイル拡張子リスト
        target_files: 取得対象のファイル名リスト

    Returns:
        List[Path]: 収集されたファイルパスのリスト
    """
    file_paths = []
    for path in root_dir.rglob('*'):
        if path.is_file():
            relative_path = path.relative_to(root_dir)
            if not any(part in exclude_dirs for part in relative_path.parts):
                if any(fnmatch.fnmatch(path.name, pattern) for pattern in EXCLUDE_FILES):
                    logger.info(f"Excluded: {path}")
                    continue
                if path.suffix in include_extensions or path.name in target_files:
                    file_paths.append(path)
    logger.info(f'Collected {len(file_paths)} files')
    return file_paths


def calculate_file_stats(file_paths: List[Path]) -> Tuple[Dict[str, Dict[str, int]], int]:
    """
    ファイル統計情報を計算する

    Args:
        file_paths: ファイルパスのリスト

    Returns:
        Tuple[Dict[str, Dict[str, int]], int]: ファイル統計情報と合計文字数
    """
    file_stats = defaultdict(lambda: {'count': 0, 'chars': 0})
    total_chars = 0
    for file_path in file_paths:
        content = read_file_content(file_path)
        extension = file_path.suffix
        file_stats[extension]['count'] += 1
        file_stats[extension]['chars'] += len(content)
        total_chars += len(content)
    return file_stats, format_number_with_commas(total_chars)


def generate_markdown_output(root_dir: Path, file_paths: List[Path], directory_structure: str) -> str:
    """
    マークダウン形式の出力を生成する

    Args:
        root_dir: ルートディレクトリ
        file_paths: ファイルパスのリスト
        tree_output: ディレクトリ構造の文字列

    Returns:
        str: マークダウン形式の出力
    """

    file_content = '## ファイル一覧\n\n'
    for file_path in file_paths:
        content = read_file_content(file_path)
        # python -m で始まるコマンドを python に変換(Claude Projectエラー対策)
        content = re.sub(r'python -m', 'python', content, flags=re.MULTILINE)
        # コードブロックの開始記号 ``` がマークダウンの区切りとして誤認識されるのを防ぐため、
        content = re.sub(r'^```', '``````', content, flags=re.MULTILINE)
        file_content += f"{file_path.relative_to(root_dir)}\n\n```{file_path.suffix}\n{content}\n```\n\n"

    return f"{directory_structure}{file_content}"


def read_file_content(file_path: Path) -> str:
    """
    ファイルの内容を読み取る

    Args:
        file_path: ファイルパス

    Returns:
        str: ファイルの内容
    """
    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        logger.error(f"UnicodeDecodeError: {file_path}")
        return ""


def is_windows():
    """
    現在のシステムがWindowsかどうかを判定する関数

    Returns:
        bool: システムがWindowsの場合はTrue、それ以外の場合はFalse
    """
    return platform.system().lower() == "windows"


def format_number_with_commas(number: int) -> str:
    """
    数値をコンマ区切りの文字列に変換する関数

    :param number: 整数または浮動小数点数
    :return: コンマ区切りの文字列
    """
    return f"{number:,}"


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
