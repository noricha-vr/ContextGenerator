import os
import subprocess
import fnmatch


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

    exclude_files = [
        "*.pyc", "*.pyo", "__pycache__", ".DS_Store", "Thumbs.db",
        "*.swp", "*.swo", "*~", ".vscode", ".idea",
        "build", "dist", "*.egg-info", "*.log", "*.bak",
        ".cache", "venv", "env", ".env", "node_modules",
        ".git", ".svn", ".hg", "local_settings.py",
        "*.pem", "*.key", "*.sqlite3", "*.db",
        "*.min.js", "*.min.css"
    ]

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
            if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_files):
                print(f"Excluded: {file_path}")
                continue

            # 拡張子のチェックまたはターゲットファイルのチェック
            if any(file.endswith(ext) for ext in include_extensions) or file in target_files:
                file_paths.append(file_path)
    print(f'Selected files: {file_paths}')
    # マークダウン形式で出力
    output_content = f"""
## ディレクトリ構造

{tree_output}

## ファイル一覧

"""

    for file_path in file_paths:
        # ファイルを開いて中身を取得
        with open(file_path, 'r') as f:
            try:
                file_content = f.read()
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError: {file_path}")
                continue

        output_content += f"""
```{file_path.replace(root_dir, "")}
{file_content.replace("```", "``````")}
```
"""
    # ファイル出力
    with open(os.path.join(output_dir, output_file), 'w') as f:
        f.write(output_content)


if __name__ == "__main__":
    root_dir = "./"  # ルートディレクトリを指定
    exclude_dirs = [".venv", ".git"]  # 除外するディレクトリ
    include_extensions = [".md", ".yaml", ".yml",
                          ".txt", ".py", ".html"]  # 含めるファイル拡張子
    output_file = "summary.md"
    output_dir = "~/Desktop"  # 出力フォルダを指定
    target_files = ["README.md", "requirements.txt",
                    "config.yaml", "Dockerfile"]  # 取得対象のファイル名を指定
    generate_summary(root_dir, exclude_dirs, include_extensions,
                     output_file, output_dir, target_files)
    print("Summary generated successfully!")
