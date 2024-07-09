import os
import subprocess
import fnmatch
from collections import defaultdict
from config import EXCLUDE_FILES


def generate_summary(root_dir: str, exclude_dirs: list[str], include_extensions: list[str], output_file: str,
                     output_dir: str, target_files: list[str]):
    """
    指定されたディレクトリ内のファイルをマークダウン形式で出力する。

    Args:
        root_dir: ルートディレクトリ
        exclude_dirs: 除外するディレクトリリスト
        include_extensions: 含めるファイル拡張子リスト
        output_file: 出力ファイル名
        output_dir: 出力フォルダ
        target_files: 取得対象のファイル名リスト
    """

    # ディレクトリ構造を tree コマンドで取得
    exclude_pattern = "|".join(exclude_dirs + ["__pycache__", "*.pyc"])
    tree_output = subprocess.check_output(
        ["tree", "-N", "-L", "4", "-I", exclude_pattern, root_dir], encoding='utf-8')

    # ファイル情報を取得
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        # 除外ディレクトリをリストから削除
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        print(f"Root: {root}")
        print(f"Dirs: {dirs}")

        for file in files:
            file_path = os.path.join(root, file)

            # 除外ファイルのチェック
            if any(fnmatch.fnmatch(file, pattern) for pattern in EXCLUDE_FILES):
                print(f"Excluded: {file_path}")
                continue

            # 拡張子のチェックまたはターゲットファイルのチェック
            if any(file.endswith(ext) for ext in include_extensions) or file in target_files:
                file_paths.append(file_path)

    print(f'Selected files: {file_paths}')

    # ファイル統計情報の初期化
    file_stats = defaultdict(lambda: {'count': 0, 'lines': 0})

    # マークダウン形式で出力
    output_content = f"""
## ディレクトリ構造

{tree_output}

## ファイル一覧

"""

    for file_path in file_paths:
        # ファイルを開いて中身を取得
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                file_content = f.read()
                # ファイル統計情報の更新
                extension = os.path.splitext(file_path)[1]
                file_stats[extension]['count'] += 1
                file_stats[extension]['lines'] += file_content.count('\n') + 1
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError: {file_path}")
                continue

        output_content += f"""
```{file_path.replace(root_dir, "")}
{file_content.replace("```", "``````")}
```
"""

    # ファイル出力
    with open(os.path.join(output_dir, output_file), 'w', encoding='utf-8') as f:
        f.write(output_content)

    return file_stats


if __name__ == "__main__":
    root_dir = "./"  # ルートディレクトリを指定
    exclude_dirs = [".venv", ".git"]  # 除外するディレクトリ
    include_extensions = [".md", ".yaml", ".yml",
                          ".txt", ".py", ".html"]  # 含めるファイル拡張子
    output_file = "summary.md"
    output_dir = "~/Desktop"  # 出力フォルダを指定
    target_files = ["README.md", "requirements.txt",
                    "config.yaml", "Dockerfile"]  # 取得対象のファイル名を指定
    file_stats = generate_summary(root_dir, exclude_dirs, include_extensions,
                                  output_file, output_dir, target_files)
    print("Summary generated successfully!")
    print("File statistics:")
    for ext, stats in file_stats.items():
        print(f"{ext}: {stats['count']} files, {stats['lines']} lines")